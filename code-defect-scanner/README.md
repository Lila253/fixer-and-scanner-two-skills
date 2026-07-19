# Code Defect Scanner

`code-defect-scanner` 是一个只读代码缺陷扫描 Skill。它扫描用户明确授权的代码范围，结合项目已有工具与语义分析，输出带代码证据、严重度和置信度的结构化缺陷报告。

本 Skill 是辅助决策工具，不是生产级静态分析器，也不能替代编译器、测试、专业安全审计或人工 Code Review。

## 核心能力

- 扫描 Git 改动、项目目录、文件、函数或粘贴代码片段。
- 根据报错堆栈聚焦相关调用路径。
- 区分 `confirmed`、`probable` 和 `hypothesis`，降低模式匹配误报。
- 输出符合 `schema_version=1.0` 的 JSON 报告和用户可读摘要。
- 保持只读，不修改源码、配置、测试或依赖文件。
- 将确认后的缺陷报告交给配套的 `code-defect-fixer`。

## 适用场景

- 提交前或 PR 缺陷检查。
- 指定文件、函数或代码片段的缺陷审查。
- 根据报错日志定位可能的错误代码。
- 接手代码时快速了解常见可靠性风险。
- 修复后的范围复检。

纯格式化、纯重构、需求分析、文档任务或只要求直接修改代码的请求不应触发本 Skill。

## 安装

1. 解压 `code-defect-scanner.zip`。
2. 保持目录结构完整，确保入口位于 `code-defect-scanner/SKILL.md`。
3. 将整个 `code-defect-scanner` 目录复制到宿主平台规定的 Skills 目录，或使用平台提供的本地 Skill 导入功能。
4. 重新加载宿主平台的 Skill 列表，然后使用 `$code-defect-scanner` 显式调用，或使用符合触发描述的自然语言请求。

不同 AI 平台的 Skill 安装路径可能不同，请以目标平台文档为准。对于 Codex 兼容环境，通常放入 `$CODEX_HOME/skills/`；未设置 `CODEX_HOME` 时通常是用户目录下的 `.codex/skills/`。

`agents/openai.yaml` 只是可选的 Codex/UI 展示元数据，不是子 Agent，也不会启动额外模型。不支持该文件的平台可以忽略它，核心入口仍是 `SKILL.md`。

## 依赖

| 类型 | 依赖 | 是否必需 | 说明 |
|---|---|---:|---|
| Skill 宿主 | 能加载 `SKILL.md` 的 AI Agent/Skill 平台 | 是 | 需要提供代码读取能力；扫描项目时还需要文件系统访问能力 |
| Python | Python 3.10+ | 条件必需 | 仅用于运行 `scripts/validate_report.py`；不运行校验脚本时核心提示流程仍可加载，但会失去确定性报告校验 |
| Python 包 | 无 | 否 | 校验脚本只使用标准库，不需要 `pip install` |
| ripgrep | `rg` | 可选，推荐 | 用于快速列举和搜索代码；缺失时可使用宿主提供的等价搜索能力 |
| Git | Git CLI | 可选 | 仅用于 Git diff、提交前扫描和变更范围识别；非 Git 目录仍可扫描指定文件或目录 |
| 项目工具 | 项目已有的测试、编译、lint、类型检查工具 | 可选 | 仅使用目标项目已经配置的工具，不会自行安装 |

本 Skill 不依赖子 Agent、MCP、数据库、云服务、外部网络 API、密钥或商业 SDK。

## 使用示例

```text
使用 $code-defect-scanner 检查当前项目的本次 Git 改动。
```

```text
使用 $code-defect-scanner 扫描 src/order_service.py，并根据下面的堆栈优先定位问题：...
```

```text
使用 $code-defect-scanner 复检刚刚修复的两个文件，不要修改代码。
```

## 报告校验

扫描报告保存为 JSON 文件后，可运行：

```text
python scripts/validate_report.py defect-report.json --source-root <项目根目录>
```

校验器会检查报告版本、字段、连续缺陷 ID、相对路径、证据行号，以及证据代码是否仍与当前源码一致。它不需要 `jsonschema` 或 PyYAML。

## 目录结构

```text
code-defect-scanner/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── references/
│   ├── defect-pattern-library.md
│   ├── defect-report-schema.json
│   ├── defect-report-template.md
│   ├── error-type-pattern-map.md
│   └── severity-standard.md
└── scripts/validate_report.py
```

## 已知限制

- 语义判断仍受模型能力、输入范围和业务上下文影响。
- 大型多语言仓库可能只能实现部分覆盖。
- `hypothesis` 只表示待验证假设，不应直接进入自动修复。
- 没有现有项目工具时，报告不能声称已经完成编译或运行时验证。
- 本 Skill 不承诺发现所有安全漏洞、并发问题或性能瓶颈。

## 许可

当前目录未附带开源许可证。公开分发前建议由作者选择合适的许可证并添加 `LICENSE` 文件。
