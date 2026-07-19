# Code Defect Fixer

`code-defect-fixer` 是一个基于证据的代码缺陷修复 Skill。它接收缺陷报告、报错堆栈或 Code Review 意见，在用户明确要求修改代码时执行最小范围修复，并报告真实验证结果。

本 Skill 是辅助开发工具，不是无人监督的生产修复系统。高风险代码、核心业务、认证授权、并发和数据迁移仍需要人工复查。

## 核心能力

- 接收 `code-defect-scanner` 的 `schema_version=1.0` JSON 报告。
- 在修改前验证报告证据是否仍匹配当前源码。
- 保护 Git 工作区已有改动，不覆盖无关文件。
- 根因不确定、文件未授权或报告过期时停止修改。
- 使用与仓库风格一致的最小补丁。
- 运行可用的目标测试、编译、lint、类型检查和 diff 检查。
- 区分实际通过、失败、跳过和未验证，不编造测试结果。

## 适用场景

- 根据缺陷报告修复指定问题。
- 根据报错堆栈定位并修改对应代码。
- 落实明确的 Code Review 修复意见。
- 修复用户已经定位的文件和函数。
- 在“检查并修复”请求中承接扫描器确认后的缺陷。

只要求解释报错、解释报告、提供方案但不要改代码、纯格式化或纯重构时，不应执行写入流程。

## 安装

1. 解压 `code-defect-fixer.zip`。
2. 保持目录结构完整，确保入口位于 `code-defect-fixer/SKILL.md`。
3. 将整个 `code-defect-fixer` 目录复制到宿主平台规定的 Skills 目录，或使用平台提供的本地 Skill 导入功能。
4. 重新加载宿主平台的 Skill 列表，然后使用 `$code-defect-fixer` 显式调用，或在请求中明确要求修改代码。

不同 AI 平台的 Skill 安装路径可能不同，请以目标平台文档为准。对于 Codex 兼容环境，通常放入 `$CODEX_HOME/skills/`；未设置 `CODEX_HOME` 时通常是用户目录下的 `.codex/skills/`。

`agents/openai.yaml` 只是可选的 Codex/UI 展示元数据，不是子 Agent，也不会启动额外模型。不支持该文件的平台可以忽略它，核心入口仍是 `SKILL.md`。

## 依赖

| 类型 | 依赖 | 是否必需 | 说明 |
|---|---|---:|---|
| Skill 宿主 | 能加载 `SKILL.md` 且支持文件编辑和命令执行的 AI Agent/Skill 平台 | 是 | 修复器必须能够读取并修改用户授权的文件 |
| Python | Python 3.10+ | 条件必需 | 仅用于运行 `scripts/validate_report.py`；Markdown/日志入口可以不运行脚本，但必须人工核对证据 |
| Python 包 | 无 | 否 | 校验脚本只使用标准库，不需要 `pip install` |
| Git | Git CLI | 可选，强烈推荐 | 用于检查脏工作区、生成实际 diff、执行 `git diff --check` 和提供回滚基础 |
| 编辑工具 | `apply_patch` 或宿主提供的等价安全编辑能力 | 是 | 必须进行最小范围修改，不能依赖覆盖式写入 |
| 项目工具 | 项目已有的测试、编译、lint、类型检查工具 | 可选 | 仅使用目标项目已经配置的工具，不会自行安装 |

本 Skill 不依赖子 Agent、MCP、数据库、云服务、外部网络 API、密钥或商业 SDK。

## 使用示例

```text
使用 $code-defect-fixer 根据 defect-report.json 修复 DEF-001，并运行可用测试。
```

```text
使用 $code-defect-fixer 根据下面的报错修改 src/order_service.py，只修改该文件：...
```

```text
使用 $code-defect-fixer 落实这些 Code Review 意见，但不要改动未列出的文件。
```

## 输入报告校验

收到扫描器 JSON 报告后，可先运行：

```text
python scripts/validate_report.py defect-report.json --source-root <项目根目录>
```

如果证据代码与当前源码不一致，校验器会拒绝旧报告，修复器不得继续按旧行号修改。校验器不需要 `jsonschema` 或 PyYAML。

## 与扫描器配套使用

```text
code-defect-scanner（只读扫描）
    -> defect-report.json
    -> code-defect-fixer（显式授权后修改）
    -> code-defect-scanner（修复后复检）
```

两个 Skill 可以独立安装。没有扫描器时，修复器仍可接收报错堆栈、Review 意见或用户明确定位的问题。

## 目录结构

```text
code-defect-fixer/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── references/
│   ├── defect-pattern-library.md
│   ├── defect-report-schema.json
│   ├── fix-summary-template.md
│   └── verification-policy.md
└── scripts/validate_report.py
```

## 已知限制

- 修复质量取决于代码上下文、接口契约和现有测试质量。
- 非 Git 目录无法提供同等级别的工作区保护和回滚基础。
- 缺少依赖或测试环境时，只能完成静态和语法级验证。
- 多文件、公共 API、数据迁移、认证授权、并发或核心业务修改需要用户先确认方案。
- 本 Skill 不适合无人监督地修改生产系统或直接发布代码。

## 许可

当前目录未附带开源许可证。公开分发前建议由作者选择合适的许可证并添加 `LICENSE` 文件。
