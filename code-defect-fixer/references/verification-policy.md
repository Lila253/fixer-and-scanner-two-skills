# 修复验证策略

## 选择顺序

1. 运行直接覆盖修改函数的单元测试或回归测试。
2. 运行同一模块或包的测试。
3. 运行项目已有的编译、类型检查、lint 和静态分析命令。
4. 运行 `git diff --check` 检查补丁格式。
5. 重新扫描受影响文件，确认原缺陷消失且没有明显新问题。

## 工具路由

- Python：优先使用仓库配置的 `pytest`、`python -m compileall`、`ruff`、`mypy` 或 `pyright`。
- JavaScript/TypeScript：读取 `package.json` 的 scripts，优先使用已有的 test、lint、typecheck、build。
- Go：优先使用 `go test`、`go vet` 和项目已有的 formatter/linter。
- Java：读取 Maven 或 Gradle 配置，使用项目已有的测试和编译任务。

不要安装工具或依赖。命令不存在时记录 `skipped`，说明原因；命令失败时记录 `failed`，不要把失败隐藏为成功。

## 风险分级

- 单文件、局部逻辑、无公共接口变化：执行目标测试和静态检查后可交付。
- 多文件、公共接口、数据迁移、认证授权、并发或核心交易：先确认方案，再扩大测试和人工复查。
- 缺少测试、缺少依赖或无法复现：可以提交补丁，但必须明确“未完成运行时验证”。
