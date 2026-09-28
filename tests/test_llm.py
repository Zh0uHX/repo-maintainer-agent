import json
import unittest
from unittest.mock import patch

from repoagent.llm import OpenAICompatibleClient, parse_json_object, parse_json_object_detail


class FakeResponse:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.value).encode()


class ParseJsonTests(unittest.TestCase):
    def test_plain_json(self):
        self.assertEqual(parse_json_object('{"ok": true}'), {"ok": True})

    def test_fenced_json(self):
        self.assertEqual(parse_json_object('```json\n{"ok": true}\n```'), {"ok": True})

    def test_embedded_json(self):
        self.assertEqual(parse_json_object('Result: {"value": 3} done'), {"value": 3})

    def test_closes_brackets_dropped_at_the_end(self):
        truncated = '{"action": {"name": "finish", "args": {"locations": [{"path": "a.py"}]}}'
        value, closed = parse_json_object_detail(truncated)
        self.assertEqual(closed, 1)
        self.assertEqual(value["action"]["args"]["locations"], [{"path": "a.py"}])

    def test_does_not_close_inside_string_or_mismatched_brackets(self):
        with self.assertRaises(ValueError):
            parse_json_object_detail('{"summary": "unterminated')
        with self.assertRaises(ValueError):
            parse_json_object_detail('{"items": [1, 2}')
        self.assertEqual(parse_json_object_detail('{"s": "a \\" {"}')[1], 0)

    def test_rejects_array(self):
        with self.assertRaises(TypeError):
            parse_json_object("[1, 2]")

    def test_client_asks_model_to_repair_malformed_json_and_counts_usage(self):
        malformed = '{"thought_summary":"inspect" "action":{"name":"diff","args":{}}}'
        corrected = '{"thought_summary":"inspect","action":{"name":"diff","args":{}}}'
        responses = [
            FakeResponse(
                {
                    "model": "provider-model",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                    "choices": [{"message": {"content": malformed}}],
                }
            ),
            FakeResponse(
                {
                    "model": "provider-model",
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": 3,
                        "total_tokens": 15,
                    },
                    "choices": [{"message": {"content": corrected}}],
                }
            ),
        ]
        client = OpenAICompatibleClient(
            model="configured-model", api_key=None, base_url="https://example.test/v1", retries=1
        )

        with patch("urllib.request.urlopen", side_effect=responses) as urlopen:
            result = client.complete([{"role": "user", "content": "Return an action."}])

        second_request = json.loads(urlopen.call_args_list[1].args[0].data)
        self.assertEqual(result["action"]["name"], "diff")
        self.assertEqual(second_request["messages"][-2]["content"], malformed)
        self.assertIn("invalid JSON", second_request["messages"][-1]["content"])
        self.assertEqual(second_request["max_tokens"], 8192)
        self.assertEqual(client.last_metadata["request_attempts"], 2)
        self.assertEqual(client.last_metadata["parse_retries"], 1)
        self.assertEqual(client.last_metadata["usage"]["total_tokens"], 30)
        self.assertNotIn("invalid_content", client.last_metadata)

    def test_exhausted_repairs_keep_the_last_invalid_reply(self):
        malformed = '{"thought_summary":"x" "action":{}}'
        response = {
            "model": "provider-model",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "choices": [{"message": {"content": malformed}}],
        }
        client = OpenAICompatibleClient(
            model="configured-model", api_key=None, base_url="https://example.test/v1", retries=1
        )
        with (
            patch(
                "urllib.request.urlopen",
                side_effect=[FakeResponse(response), FakeResponse(response)],
            ),
            self.assertRaises(RuntimeError),
        ):
            client.complete([{"role": "user", "content": "Return an action."}])
        self.assertEqual(client.last_metadata["parse_retries"], 2)
        self.assertEqual(client.last_metadata["invalid_content"], malformed)

    def test_empty_reply_resends_original_request(self):
        def reply(content):
            return FakeResponse(
                {
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                    "choices": [{"message": {"content": content}}],
                }
            )

        client = OpenAICompatibleClient(
            model="configured-model", api_key=None, base_url="https://example.test/v1", retries=1
        )
        original = [{"role": "user", "content": "Return an action."}]
        with (
            patch("urllib.request.urlopen", side_effect=[reply("   "), reply('{"ok": 1}')]) as call,
            patch("time.sleep"),
        ):
            self.assertEqual(client.complete(original), {"ok": 1})
        first, second = (json.loads(item.args[0].data) for item in call.call_args_list)
        self.assertEqual(second["messages"], original)
        self.assertIn("response_format", first)
        self.assertNotIn("response_format", second)
        self.assertTrue(client.last_metadata["json_mode_fallback"])
        self.assertEqual(client.last_metadata["parse_retries"], 0)
        self.assertEqual(client.last_metadata["request_attempts"], 2)


if __name__ == "__main__":
    unittest.main()
