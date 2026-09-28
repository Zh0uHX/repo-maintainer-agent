# W1 B1 首次运行记录

## 1. 环境与复现
代码版本：`bbc55d6d3831b0d3b146222e0f543867de26376f`（`docs: bootstrap NOTES structure`）
测试：make test
结果：通过
摘要：Ran 43 tests in 0.648s

| 评测 | 通过 | 平均步数 | 总 token | 报告 |
|---|---:|---:|---:|---|
| smoke 本次 | 2/2 | 7.0 | 19976 | reports/b1-smoke.md |
| pilot 原报告 | 10/10 | 6.9 | 95,906 | reports/pilot-ast.md |
| pilot 本次 | 10/10 | 7.8 | 114,022 | reports/pilot-ast-repro.md |

观察：通过率一致；本次 pilot 平均多 0.9 步、18,116 token。
思考：
1. 步数和token数不一致：平均步数和token数取决于agent实际走的路径，虽然模型请求设置了tmperature=0，但是没有固定随机种子，模型实际执行步骤也可能发生变化。

待查：哪些用例多走了步骤？对照每个用例的 trace，不凭总数猜原因。

## 2. 一条完整 trace 的逐轮注解
用例：`locate-cache-falsey-value-bug`（归档的 navigation AST 评测，不是本次 pilot 复现）。

本次运行收到的任务：修复 `Cache.get_or_set`，使已缓存的 `0`、`False`、空字符串不再重复调用 loader，同时保留缓存未命中时的行为。源文件：[`trace.jsonl`](../reports/navigation-ast-artifacts/locate-cache-falsey-value-bug/.repoagent/runs/20260806T093936Z-99fe9424/trace.jsonl)；运行结果：[`result.json`](../reports/navigation-ast-artifacts/locate-cache-falsey-value-bug/.repoagent/runs/20260806T093936Z-99fe9424/result.json)；评测结果：[`navigation-ast.json`](../reports/navigation-ast.json)。

完整 trace 共 21 条事件：`run_started`，规划阶段的 `model_response` 与 `plan`，第 1–8 轮各一条 `model_response` 和 `tool_observation`，第 9 轮的 `model_response` 与 `finish`。共 10 次模型响应、8 次工具调用。下表“为什么接着这样做”是依据相邻事件做的人工推断；`thought_summary` 只是模型给出的简短可见理由。

| 阶段/轮次 | Agent 想做什么 | 工具和关键参数 | 实际返回 | 为什么接着这样做 |
|---|---|---|---|---|
| plan | 先定位方法和缓存命中判断，再修复、补测、运行检查。 | 规划模型请求；无仓库工具调用。 | `goal`、`steps`、`risks`、`checks` 被记录为 `plan`。 | 计划首步是定位 `get_or_set`，所以先查目标文件的符号。 |
| 1 | 定位 `Cache.get_or_set`。 | `inspect_python(path="cache/core.py")` | 返回 `Cache.get_or_set` 位于第 5–10 行，另有类和构造函数；`ok=true`。 | AST 只给符号位置和签名，尚不知道判断条件；下一轮读源码。 |
| 2 | 查看命中与未命中的具体实现。 | `read_file(path="cache/core.py", start_line=1, end_line=20)` | 第 6–9 行是 `cached = self.values.get(key)`、`if not cached:`、调用 loader、写回缓存。 | `if not cached` 会把 `0`、`False`、`''` 当成未命中；已有足够证据做定点修改。 |
| 3 | 将真假值判断改为 key 是否存在。 | `edit_file(path="cache/core.py", old_text=原方法体, new_text=按 key 存在性判断)` | `applied=true`；diff 显示改为 `if key not in self.values: self.values[key] = loader()`，最后返回 `self.values[key]`。 | 源码修复已应用，但还需覆盖三种假值；转去检查现有测试。 |
| 4 | 找测试函数的位置。 | `inspect_python(path="tests/test_cache.py")` | 仅找到 `test_zero_is_a_cached_value`（第 3–8 行）。 | 已有 `0` 用例，但还不知道断言写法；下一轮读取完整测试。 |
| 5 | 查看测试风格和现有断言。 | `read_file(path="tests/test_cache.py", start_line=1, end_line=20)` | 测试预置缓存值 `0`，断言返回 `0` 且 loader 没被调用。 | 沿用相同模式，可以补 `False` 与空字符串用例。 |
| 6 | 添加另两种假值的测试。 | `edit_file(path="tests/test_cache.py", old_text=原测试, new_text=原测试加两个新测试)` | `applied=true`；新增 `False` 和 `''` 的返回值、loader 调用次数断言。 | 代码与测试均已改动，下一步运行测试验证。 |
| 7 | 验证修复。 | `run_check(command="pytest tests/test_cache.py -q")` | `ok=true`、`exit_code=0`、`3 passed in 0.01s`。 | 可见测试通过；下一步看完整 diff，检查实际改动范围。 |
| 8 | 审核本次改动。 | `diff()` | `truncated=false`；diff 包含 `cache/core.py` 和 `tests/test_cache.py` 两个文件。 | Agent 认为修复很小且测试通过，于是结束；评测器稍后会将测试文件改动判为越界。 |
| 9 | 报告完成。 | `finish(status="completed", summary=...)`；这不是工具调用。 | `finish` 事件记下 `completed`；此轮没有 `tool_observation`。 | 循环终止，随后由评测器独立检查结果。 |

**结果核对：** `result.json` 中 Agent 状态为 `completed`，修改了两个文件，内部测试 3/3 通过。`navigation-ast.json` 中该用例 `passed=false`：评测允许修改的文件只有 `cache/core.py`，但第 6 轮还改了 `tests/test_cache.py`。评测器额外执行的完整测试 5/5 通过，所以失败原因是**改动范围不合约束**，不是功能测试失败。Agent 的 `finish` 不能替代评测器的 `passed`。

**最关键的决策：**第 3 轮基于第 2 轮看到的 `if not cached`，把判断改为 `key not in self.values`；这直接修复了假值被误判为缓存未命中的原因。评测失败点是第 6 轮修改测试文件：第 8 轮 diff 已明确展示这一点，但 Agent 仍在第 9 轮结束。

**证据边界：**这份归档 trace 的 `run_started.task` 没写“不要修改已有测试”，但对应评测报告的 `allowed_changed_files` 只允许 `cache/core.py`；当前 `evals/navigation.jsonl` 的同名任务文本则明确写了该限制。因此可以确定评测失败的直接原因，不能据此断言这次运行的模型忽略了当轮提示中的自然语言禁令。此 trace 也不是本次 pilot 复现的运行记录。

## 3. 在 RepoAgent 自身仓库上的手写任务
任务与验收条件：repoagent eval 在指定 --artifacts 时，成功用例结束后也应保留完整 trace.jsonl。添加无需外部模型的回归测试；保持 passed/status 判定、失败用例 artifacts 和未指定 --artifacts 时的行为不变。不要修改 evals/*.jsonl。运行相关测试并报告结果。
实际修改、检查结果、trace 路径：修改了文件tests/test_evals.py和repoagent/evals.py，Agent 运行结果：达到 18 步上限，status=failed；未执行测试（checks=[]）。人工补充 `import json` 后，全量测试 44/44 通过；trace 已归档到[trace.jsonl](../reports/b1-self-run-20260928T053211Z-e0ece8c5/trace.jsonl)。
在真实仓库上观察到的能力或失败：模型花了非常多步骤用于定位文件和检查trace是否被截断，没有调用run_check，也没有发出finish。

## 4. 十一条设计决策的验证
| # | 决策 | 代码位置 | 我做了什么 | 实际观察 | 恢复/结论 |
|---|---|---|---|---|---|
| 1 | 完成门控 | repoagent/agent.py的line 191| 将`if status == "completed" and tools.checks:`改为`if False and status == "completed" and tools.checks:` 随后运行`/Users/rickzhou/Code/Codex/Agent/.venv/bin/python -m pytest tests/test_agent.py::AgentTests::test_cannot_report_completed_after_failed_final_check -q`| 测试安排了一次失败的run_check，但模型声明为finish，外部pytest发现测试结果不是预期的failed就产生了报错，说明门控机制有效 | 最后一次检查失败时，门控机制会把模型声称的 completed 改为 failed；关闭门控后出现“检查失败却报告完成”，测试因此失败。它的局限是：Agent 若根本不运行检查，这段门控不会触发。 |
| 6 | `edit_file` 的唯一匹配约束 | `repoagent/tools.py:281–288` | 原版定向测试 1 passed；将 `count != 1` 临时改为 `count < 1`，运行 `test_edit_requires_unique_match`；再恢复原条件并重跑。 | 改坏后测试 1 failed：`ToolError not raised`；恢复后 1 passed。重复的 `old_text` 不再被拒绝，工具会走到只替换第一处的逻辑。 | 唯一匹配避免含糊编辑；本实验验证的是工具约束，没有验证模型遇错后是否会增加上下文重试。实验源码已恢复。 |
| 11 | 连续错误熔断 | `repoagent/agent.py:185–188`；`tests/test_agent.py:76–77` | 原版测试 1 passed；临时增加 `result.metrics["steps"] == 4` 断言并确认通过；将阈值 `>= 4` 改为 `>= 1` 后重跑；移除断言再测；最后恢复阈值。 | 带步数断言时测试 1 failed：实际 `steps=1`，预期 4；移除临时断言后，阈值仍为 1 的原测试却通过；源码恢复后测试再次通过。 | 熔断阈值确实决定连续错误后何时停止。现有测试只断言 `failed` 和固定摘要，未覆盖实际停止步数，因而漏检阈值错误。临时改动均已恢复。 |

其余 #2–#5、#7–#10 尚未验证。

