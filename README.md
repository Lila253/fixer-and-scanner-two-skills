# DefectLoop

证据驱动的代码缺陷扫描与修复双 Skill 闭环。

DefectLoop 由 `code-defect-scanner` 和 `code-defect-fixer` 两个可独立安装、可串联使用的 Skill 组成。它把代码缺陷处理拆分为只读发现、结构化交接、授权修复和修复后复检，既保留安全边界，也形成完整开发工作流。

当前版本：`1.0.1`，详见 [`version.json`](version.json)。

## 为什么是双 Skill

扫描和修复具有不同权限：扫描器应保持只读，修复器只有在用户明确要求修改时才能写入代码。将它们拆分后，通过同一个 `schema_version=1.0` JSON 报告衔接，可以避免扫描阶段意外改代码，也允许用户只安装其中一个组件。

```mermaid
flowchart LR
    A[用户代码或 Git 改动] --> B[code-defect-scanner]
    B --> C[证据化 defect-report.json]
    C --> D[code-defect-fixer]
    D --> E[最小代码补丁与验证结果]
    E --> B
```

## 组件

| Skill | 权限 | 主要职责 | 文档 |
|---|---|---|---|
| `code-defect-scanner` | 只读 | 扫描代码、区分确认缺陷与待验证风险、生成结构化报告 | [查看 README](code-defect-scanner/README.md) |
| `code-defect-fixer` | 显式授权后写入 | 校验报告新鲜度、分析根因、执行最小修复、报告真实验证结果 | [查看 README](code-defect-fixer/README.md) |

两个 Skill 不依赖子 Agent、MCP、云服务、外部网络 API 或第三方 Python 包。

## 下载安装

### 安装整套 Skill

下载 [`packages/defectloop-1.0.1.zip`](packages/defectloop-1.0.1.zip)，解压后将两个 Skill 目录分别导入宿主平台：

```text
code-defect-scanner/
code-defect-fixer/
```

### 单独安装

- [`packages/code-defect-scanner.zip`](packages/code-defect-scanner.zip)
- [`packages/code-defect-fixer.zip`](packages/code-defect-fixer.zip)

保持每个 Skill 的目录结构完整，核心入口均为各自的 `SKILL.md`。不同平台的导入路径可能不同，请以目标平台文档为准。

## 快速体验

扫描请求：

```text
使用 $code-defect-scanner 检查当前项目的本次 Git 改动，只报告有代码证据的问题。
```

修复请求：

```text
使用 $code-defect-fixer 根据 defect-report.json 修复已确认缺陷，并运行可用验证。
```

组合请求：

```text
先扫描这个文件，再修复确认的问题，最后重新扫描验证。
```

## 可复现演示

[`examples/end-to-end-demo`](examples/end-to-end-demo) 提供带缺陷代码、扫描报告、修复后代码和测试结果。

验证扫描报告：

```text
python code-defect-scanner/scripts/validate_report.py examples/end-to-end-demo/defect-report.json --source-root examples/end-to-end-demo
```

运行修复后行为测试：

```text
python examples/end-to-end-demo/test_demo.py
```

## 报告协议

扫描器和修复器共享 [`defect-report-schema.json`](code-defect-scanner/references/defect-report-schema.json)。报告包含：

- 连续的 `DEF-*` 缺陷 ID。
- 相对文件路径、准确行号和当前代码证据。
- `defect`、`risk`、`suggestion` 类型。
- `confirmed`、`probable`、`hypothesis` 状态。
- 严重度、置信度、影响假设和处理方向。
- 实际运行工具的 `passed`、`failed`、`skipped` 状态。

修复器在修改前重新校验证据；如果源码已经变化，旧报告会被拒绝，避免按过期行号修复。

## 依赖

| 依赖 | 要求 |
|---|---|
| Skill 宿主 | 能加载 `SKILL.md`；扫描项目需要读取能力，修复需要安全编辑能力 |
| Python | 3.10+，仅用于报告校验器和演示测试 |
| 第三方 Python 包 | 无 |
| Git | 可选；变更扫描和修复工作区保护时推荐 |
| ripgrep (`rg`) | 可选；用于快速文件发现和搜索 |
| 项目测试/lint/构建工具 | 可选；只使用项目已有工具，不自行安装 |

## 测试状态

| 测试 | 结果 |
|---|---|
| Skill 结构和触发边界 | 通过 |
| 合法报告跨 Skill 校验 | 通过 |
| 畸形 JSON、路径穿越、低证据 P0 | 正确拒绝 |
| 扫描、修复、行为回归、复检闭环 | 通过 |
| 旧报告失效检测 | 通过 |
| 校验器重复运行 100 次 | 100/100 通过 |
| ZIP 安装结构 | 通过 |
| AstronClaw 实机部署 | 待在目标运行环境验证 |

详细结果见 [`examples/end-to-end-demo/test-results.md`](examples/end-to-end-demo/test-results.md)。

## 安全设计

- 扫描器不得修改源码、配置、测试或依赖。
- 修复器没有明确修改意图时不得写文件。
- 报告和证据路径必须是扫描根目录内的安全相对路径。
- 根因不确定、报告过期或文件未授权时停止修改。
- 不自行安装依赖，不编造测试、覆盖率或副作用结论。
- 敏感文件默认不读取；明确检查时也必须遮盖密钥值。

## 版本管理

根目录 [`version.json`](version.json) 是版本权威文件，采用语义化版本：

- `MAJOR`：报告协议或使用方式存在不兼容变更。
- `MINOR`：新增兼容能力、模式或工作流。
- `PATCH`：修正文档、规则、脚本或兼容问题。

更新组件时同步修改套件版本、对应组件版本和 `updated_at`。

## 项目结构

### GitHub 仓库

```text
fixer-and-scanner-two-skills/
├── README.md
├── version.json
├── code-defect-scanner/
├── code-defect-fixer/
├── examples/end-to-end-demo/
├── packages/
└── .gitignore
```

### 整套 ZIP 解压后

`defectloop-1.0.1.zip` 不包含 Git 元数据、独立组件 ZIP 或仓库配置文件，解压结构如下：

```text
defectloop-1.0.1/
├── README.md
├── version.json
├── code-defect-scanner/
├── code-defect-fixer/
└── examples/end-to-end-demo/
```

## 当前定位

DefectLoop 是辅助开发型工具，不是无人监督的生产静态分析或自动修复系统。大型仓库、安全关键系统、核心交易、认证授权、并发和数据迁移仍需专业工具与人工复查。
