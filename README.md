# CodeForge

一个用 Python 从零构建的**终端 AI 编程助手**（定位类似 Claude Code），在终端里与大型语言模型对话、读写代码、执行命令、调用 MCP 与 Skill，并支持多 Agent 团队协作。基于 [Textual](https://textual.textualize.io/) 构建交互式 TUI，内置完整的权限控制、Hook、记忆、Git Worktree 与沙箱机制。

> 本项目以 **CodeForge** 对外发布，Python 包名、CLI 命令与配置目录已统一为 `codeforge` / `.codeforge/`。

---

## ✨ 特性

- **多模型供应商**：内置 `anthropic`、`openai`、`openai-compat` 三种协议，可通过 YAML 配置切换，支持 `thinking`（extended thinking）开关。
- **交互式 TUI**：Textual 终端界面，流式输出、多轮上下文、会话管理。
- **完整工具链**：文件读/写/编辑、Bash、grep/glob、diff、Skill 加载与安装、工具检索、Git Worktree 切换。
- **多 Agent 团队**：Lead + Teammate 协作，基于邮箱投递消息、共享任务板，支持 tmux / iTerm2 / 进程内三种后端。
- **Agent 编排**：可派生子 Agent（fork）、任务管理器、执行轨迹、通知回传、协调者模式、验证 Agent。
- **MCP 支持**：连接 stdio 与 Streamable HTTP 两类 MCP Server，动态注册工具。
- **权限与安全**：四种权限模式（`default` / `acceptEdits` / `plan` / `bypassPermissions`），危险命令检测、路径沙箱、规则引擎、可选 OS 级沙箱（bwrap / seatbelt）。
- **Hook 系统**：事件驱动的可配置 Hook（如工具调用前/后），支持条件与外部命令执行。
- **记忆系统**：自动记忆、整合、召回、会话记忆与项目指令加载。
- **Git Worktree**：隔离分支工作区，自动清理过期 Worktree，保留 `node_modules` 等目录的符号链接。
- **远程模式**：启动 WebSocket 服务，浏览器直接访问 `http://localhost:18888` 使用。
- **非交互模式**：`-p` 直接执行提示词，支持 `text` 与 `stream-json`（NDJSON 事件流）两种输出格式，便于脚本集成。

---

## 🧱 架构总览

```
┌──────────────────────────────────────────────────────────────┐
│                          TUI (Textual)                       │
│              CodeForgeApp · 斜杠命令 · 会话 · 对话窗口            │
└───────────────┬──────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│                        Agent 主循环                            │
│        事件流 (StreamText/ToolUse/ToolResult/Usage/...)        │
│                多轮上下文 · 压缩 · 重试 · 轨迹                  │
└───────┬──────────────┬───────────────┬──────────────┬────────┘
        │              │               │              │
┌───────▼─────┐ ┌──────▼──────┐ ┌───────▼───────┐ ┌────▼────────┐
│  Provider    │ │  Tool 注册表 │ │ 权限检查器     │ │ MCP 管理器  │
│ anthropic/   │ │ 文件/Bash/  │ │ 模式·沙箱·规则 │ │ stdio/http  │
│ openai/compat│ │ 检索/Skill/ │ │ 危险命令检测   │ │ 工具注册     │
│              │ │ Agent/Team  │ │              │ │             │
└──────────────┘ └──────┬──────┘ └──────────────┘ └─────────────┘
                        │
        ┌───────────────▼───────────────────────────────┐
        │         记忆 · Hook引擎 · Worktree · 团队协调    │
        │         多 Agent 分叉 / 队友邮箱 / 任务板       │
        └───────────────────────────────────────────────┘
```

---

## 环境要求

- Python **>= 3.11**
- 一个可用的 LLM API（Anthropic Claude / OpenAI 或兼容接口）

---

## 安装

```bash
# 使用 uv（推荐）
uv sync --group dev

# 或使用 pip
pip install -e .
```

安装后即获得 `codeforge` 命令（对应包内脚本入口 `codeforge.__main__:main`）。

### 运行测试

```bash
pytest
```

---

## 配置

CodeForge 按以下顺序加载并**合并** YAML 配置（后层覆盖前层）：

1. `~/.codeforge/config.yaml`（全局）
2. `.codeforge/config.yaml`（项目）
3. `.codeforge/config.local.yaml`（本地，不入库）

`providers` 为必填项，至少配置一个供应商：

```yaml
providers:
  - name: claude
    protocol: anthropic          # anthropic | openai | openai-compat
    base_url: https://api.anthropic.com
    model: claude-sonnet-4-5
    api_key: ""                  # 留空则回退到环境变量 ANTHROPIC_API_KEY
    thinking: false              # 可选，启用 extended thinking
    # context_window: 200000     # 可选，显式覆盖；否则自动探测/内置映射表/默认值
    # max_output_tokens: 8192    # 可选，默认 thinking 64000 / 其余 8192

permission_mode: default          # default | acceptEdits | plan | bypassPermissions

mcp_servers:                      # 可选，MCP 工具扩展
  - name: my-mcp
    command: npx
    args: ["-y", "some-mcp-server"]
    # 或使用远程 server：
    # url: http://localhost:3000/mcp
    # headers: { "Authorization": "Bearer ..." }

enable_fork: true                 # 允许派生子 Agent
enable_verification_agent: false  # 启用验证 Agent
enable_coordinator_mode: false    # 协调者模式（收窄工具集）

worktree:
  symlink_directories: ["node_modules", ".venv", "vendor"]
  stale_cleanup_interval: 3600    # 过期清理间隔（秒）
  stale_cutoff_hours: 24          # 超过该时长视为过期

sandbox:
  enabled: false                  # 启用 OS 级沙箱（Linux bwrap / macOS seatbelt）
  auto_allow: false
  network_enabled: false

hooks:                            # 可选，事件 Hook（详见下文）
  - event: PreToolUse
    condition: ...
    command: ...
```

> 配置结构会经过校验器校验，缺失字段、非法协议或非法的 `permission_mode` 会在启动时报错退出。

### 权限模式

| 模式 | 读文件 | 写文件/编辑 | 执行命令 |
|------|:---:|:---:|:---:|
| `default` | 允许 | 询问 | 询问 |
| `acceptEdits` | 允许 | 允许 | 询问 |
| `plan` | 允许 | 询问 | 询问 |
| `bypassPermissions` | 允许 | 允许 | 允许 |

此外，权限系统内置**危险命令检测**与**路径沙箱**（限定在工作目录内读写），并支持通过 `permissions.yaml` / `permissions.local.yaml` 自定义规则（用户级、项目级、本地级）。

---

## 使用

### 交互式 TUI

```bash
codeforge
```

进入终端对话界面，输入自然语言即可。内置斜杠命令：

| 命令 | 说明 |
|------|------|
| `/help` (`/h`, `/?`) | 显示帮助 |
| `/clear` | 清空对话 |
| `/compact` | 压缩上下文 |
| `/mcp` | 管理 MCP 服务器 |
| `/memory` | 记忆管理 |
| `/permission` | 权限管理 |
| `/plan` | 规划模式 |
| `/review` | 审查 |
| `/rewind` | 回退对话 |
| `/sandbox` | 沙箱管理 |
| `/session` | 会话管理 |
| `/skill` | Skill 管理 |
| `/skill_register` | 注册 Skill |
| `/status` | 状态查看 |
| `/tasks` | 任务管理 |
| `/trace` | 执行轨迹 |
| `/worktree` | Worktree 管理 |

### 非交互模式

```bash
# 直接执行提示词，打印最终文本
codeforge -p "帮我解释这段代码的作用"

# 输出 NDJSON 事件流（assistant/thinking/tool_use/tool_result/usage/result ...）
codeforge -p "重构一下 main.py" --output-format stream-json
```

### 指定权限模式

```bash
codeforge --mode plan
codeforge --mode bypassPermissions
```

### 远程模式（浏览器 UI）

```bash
codeforge --remote
```

启动 WebSocket 服务（`0.0.0.0:18888`），浏览器访问 `http://localhost:18888` 即可使用。

---

## 🤝 多 Agent 团队

CodeForge 支持 **Lead + Teammate** 协作：由 Lead 组建团队并派发任务，Teammate 以独立 worker 进程运行（`--teammate`），通过**邮箱**投递消息、通过**共享任务板**（`tasks.json`）同步任务，并将结果通知回传 Lead。

```bash
# 在 tmux / iTerm2 窗格中作为队友 worker 启动
codeforge --teammate --team-name <team> --agent-name <agent>
```

- 支持 `in-process`、tmux、iTerm2 三种队友后端（`teammate_mode` 配置）。
- 可选 `enable_coordinator_mode`：从第一轮起收窄工具集，只保留协调所需工具。
- 队友层不再向下派生子 Agent，组建/解散团队是 Lead 的职责。

---

## 🧰 Skill 系统

- 内置 Skill 位于 `codeforge/skills/builtins/`，项目级 Skill 放在 `.agents/`。
- 支持 `/skill` 安装与加载、`/skill_register` 注册；Skill 可在声明 fork 模式时退回 inline 执行。

---

## 🔌 Hook 系统

事件驱动的可配置 Hook（如 `PreToolUse`、`PostToolUse` 等），每个 Hook 可声明**条件**（condition）与**执行器**（command / 外部程序），在 Agent 主循环的关键节点触发。配置见上文 `hooks` 段。

---

## 🧠 记忆系统

- 自动记忆（`auto_memory`）：将对话中的关键信息沉淀为长期记忆。
- 记忆整合（`consolidation`）：定期整合去重。
- 召回（`recall`）：基于上下文的记忆检索。
- 会话记忆（`session`）与项目指令（`instructions`，如 `AGENTS.md`）加载。

---

## 📂 项目结构

```
codeforge/
├── agent.py            # Agent 主循环与事件流
├── app.py              # Textual TUI 应用
├── client.py           # Provider 客户端抽象
├── config.py           # 配置加载与合并
├── validator.py        # 配置校验
├── __main__.py         # CLI 入口（含 -p / --remote / --teammate）
├── remote.py           # WebSocket 远程模式
├── agents/             # 子 Agent / 任务 / 轨迹 / 工具过滤
├── commands/           # 斜杠命令注册与处理器
├── context/            # 上下文管理
├── filehistory/        # 文件历史
├── hooks/              # Hook 引擎
├── mcp/                # MCP 客户端与工具包装
├── memory/             # 自动记忆 / 整合 / 召回 / 会话
├── permissions/        # 权限模式 / 危险命令 / 沙箱 / 规则
├── sandbox/            # OS 级沙箱（bwrap / seatbelt）
├── skills/             # Skill 安装 / 加载 / 执行
├── teams/              # 多 Agent 团队协调 / 邮箱 / 任务板
├── tools/              # 内置工具与工具检索
└── worktree/           # Git Worktree 管理
tests/                  # pytest 测试套件
```

---

## 开发说明

- 代码规范：变量命名使用 `snake_case`，提交信息使用英文。
- 开发环境：`uv` + `pyproject.toml`，构建后端为 `hatchling`。
- 主要依赖：`textual`、`anthropic`、`openai`、`pyyaml`、`pydantic`、`mcp`、`httpx`、`websockets`。
- 端到端验证建议在 `tmux` 中启动并输入真实对话请求，观察工具调用与回复生成是否符合预期。

---

## 命名说明

本项目对外以 **CodeForge** 发布。此前代码使用内部代号 `mewcode`，发布前已全局统一改为 `codeforge`：包括 Python 包名、CLI 命令、配置目录 `.codeforge/` 及全部文档示例。项目结构见上文目录树（`codeforge/` 为核心包）。

---

## 许可证

本仓库当前未附带 LICENSE 文件。发布到 GitHub 前请先选择合适的开源许可证（如 MIT、Apache-2.0）并添加 `LICENSE` 文件。
