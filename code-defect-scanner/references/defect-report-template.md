# 缺陷报告输出模板

以 `defect-report-schema.json` 对应的 JSON 为权威数据；Markdown 只提供用户可读摘要。不得只输出 Markdown 后声称报告可被修复器可靠解析。

## 用户可读摘要

```markdown
## 代码缺陷扫描报告

- 扫描范围：{scope}
- 文件覆盖：{files_scanned} 个文件，{complete|partial}
- 工具结果：{实际运行命令及 passed/failed/skipped 摘要}
- 缺陷：{confirmed/probable 数量及 P0-P3 分布}
- 待确认：{hypothesis 数量}
- 跳过项：{路径与原因；没有则写“无”}

### DEF-001 · {标题}
- 位置：{path}:{start_line} / {symbol}
- 类型：{kind} · {category}
- 状态：{confirmed|probable|hypothesis}
- 严重度：{P0|P1|P2|P3|未定}
- 置信度：{high|medium|low}
- 影响假设：{用于定级的业务或可达性假设}
- 证据：`{path}:{line} {code}`
- 处理方向：{只给方向，不给补丁}
```

## 权威 JSON

```json
{
  "schema_version": "1.0",
  "scan": {
    "scope": "src/service.py",
    "files_scanned": 1,
    "coverage": "complete",
    "skipped": [],
    "error_hint": null
  },
  "findings": [
    {
      "id": "DEF-001",
      "path": "src/service.py",
      "start_line": 42,
      "end_line": 42,
      "symbol": "load_profile",
      "kind": "risk",
      "category": "null-dereference",
      "status": "probable",
      "severity": "P2",
      "confidence": "medium",
      "description": "仓库查询结果可能为空，但代码直接读取字段。",
      "impact_assumption": "repo.find 在记录不存在时返回 None。",
      "evidence": [
        {"path": "src/service.py", "line": 42, "code": "return profile[\"name\"]"}
      ],
      "suggested_action": "确认接口契约并在字段访问前处理空结果。"
    }
  ],
  "tool_results": [
    {"command": "python -m compileall src", "status": "passed", "summary": "源码语法检查通过。"}
  ]
}
```

`hypothesis` 仍使用连续的 `DEF-*` 编号，但必须在摘要的“待确认”部分单独列出。`suggestion` 不计入缺陷总数。
