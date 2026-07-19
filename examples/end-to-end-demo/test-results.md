# End-to-End Demo Test Results

测试日期：2026-07-19  
运行环境：Windows、Python 3.12.4

## 场景

`buggy-code.py` 包含两个扫描目标和一个安全对照函数：

- `find_name`：外部查询结果可能为空，属于 `probable` 风险。
- `print_items`：循环上界多一次，属于 `confirmed` 越界缺陷。
- `safe_find_name`：已经处理空结果，不应被误报。

## 扫描报告校验

```text
python code-defect-scanner/scripts/validate_report.py examples/end-to-end-demo/defect-report.json --source-root examples/end-to-end-demo
```

预期结果：报告字段、连续 ID、相对路径、行号和代码证据全部通过。

## 修复后行为测试

```text
python examples/end-to-end-demo/test_demo.py
```

预期结果：

```text
DefectLoop end-to-end demo: all behavior checks passed
```

覆盖路径：查询结果为空、查询结果正常、空列表、两元素列表和安全对照函数。

## 鲁棒性与安全测试

- 畸形 JSON：拒绝。
- 路径穿越 `../outside.py`：拒绝。
- `hypothesis` 直接标记为 P0：拒绝。
- 修复后继续使用旧证据报告：拒绝。
- 两个报告校验器重复运行 100 次：100/100 通过。
- ZIP 中缓存、临时夹具和 `.pyc`：未发现。

## 尚未验证

当前开发环境没有 AstronClaw CLI 或对应运行时，因此尚未完成 AstronClaw 实机部署与调用测试。该项必须在赛事环境补测后更新 `version.json` 的 `runtime.astronclaw_validation`。
