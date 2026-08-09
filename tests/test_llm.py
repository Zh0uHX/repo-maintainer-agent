import json
import unittest
from unittest.mock import patch

from repoagent.llm import OpenAICompatibleClient, parse_json_object


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


if __name__ == "__main__":
    unittest.main()
