# Repo to Interview Skill

[English](README.md) | 中文

一个面向真实团队项目的 Agent Skill：自动阅读代码库、重建架构、追踪 Agent 执行链、筛选高价值源码，并生成适合简历与技术面试使用的项目档案。

它尤其适合实习、校招和团队研发场景：代码库里通常包含大量团队共同完成的模块，真正困难的不是“把项目写得更好看”，而是搞清楚 **项目到底怎么工作、哪些技术点最值得讲、面试官会追问到哪里、自己应该重点复习哪些代码**。

## 这个 Skill 解决什么问题

普通简历工具通常从用户自己写的一段项目描述开始优化，这会带来两个问题：

1. 很多真正有技术含量的内容没有被写出来；
2. 很容易把团队能力和个人表述混在一起，导致面试时扛不住追问。

这个 Skill 采用相反的流程：

```text
代码库
  ↓
AST 静态分析
  ↓
Import / Call Graph
  ↓
Agent 执行链追踪
  ↓
面试价值评分
  ↓
架构与技术点重建
  ↓
project_profile.md
  ↓
简历 / 面试包装
```

## 当前核心能力

### 1. Python / TypeScript AST 解析

对 Python、TypeScript、TSX 源码做结构化静态分析，而不是只靠关键词搜索。

Python 使用标准库 `ast`，提取：

- import / from-import；
- function / async function；
- class / method；
- decorator；
- 函数和方法调用；
- 源码行范围；
- Agent / LLM / evaluation / tracing 等技术信号。

TypeScript / TSX 使用 TypeScript Compiler API，提取：

- import / export；
- function / method / class；
- 变量绑定的 arrow function；
- call expression；
- decorator；
- 关键标识符和字符串信号。

如果单个文件解析失败，不会中断整个仓库分析，而是记录错误后继续。

### 2. Import Graph / Call Graph 构建

自动构建两类图：

#### Import Graph

文件作为节点，内部 import 作为边。

可以帮助识别：

- 核心模块；
- 高耦合模块；
- 架构入口；
- service / registry / router 等桥接层；
- 上下游依赖关系。

#### Call Graph

函数 / 方法作为节点，调用关系作为边。

调用边会附带置信度：

- `high`：同文件或可明确解析的调用；
- `medium`：较可信的跨模块限定调用；
- `low`：只能通过静态启发式判断。

由于依赖注入、动态分发、反射、装饰器、事件总线、Tool Registry 等机制无法完全通过静态分析还原，因此 Skill 不会把低置信度调用强行描述成确定的运行时事实。

### 3. Agent 执行链自动追踪

针对 Agent / LLM 项目，自动寻找代表性的执行路径。

重点识别：

- Agent / Planner / Executor / Orchestrator；
- Tool Calling / Function Calling；
- Tool Registry；
- Prompt 构建；
- LLM / Chat / Completion 调用；
- Context / Session / Memory；
- Structured Output；
- Evaluation / LLM-as-a-Judge；
- Trace / Span / OpenTelemetry；
- Retry / Fallback / Routing；
- Streaming / Token / Latency / Cost。

执行链会尽量从真实入口开始，例如：

```text
API Handler
→ Conversation Service
→ Diagnosis Agent
→ Tool Registry
→ Tool Execution
→ Model Decision
→ State Persistence
→ Evaluator / Tracing
```

如果静态分析中间存在无法确定的动态跳转，会明确标记：

```text
[dynamic/unresolved]
```

而不是猜测。

### 4. 自动计算「面试价值分」

每个源码文件会获得一个 0-100 的面试价值评分，用来回答一个非常实际的问题：

> 面试前时间有限，我最应该重新看哪些代码？

默认评分维度：

| 维度 | 分值 |
|---|---:|
| Agent / LLM 相关性 | 30 |
| 核心执行链重要性 | 25 |
| Import / Call Graph 中心性 | 20 |
| 架构信号 | 15 |
| 实现深度 | 10 |

同时会对以下内容降权：

- generated / vendor 代码；
- 与核心机制关系不大的 test / fixture；
- 纯配置文件；
- 解析失败文件；
- 仅存在低置信度证据的文件。

评分区间：

- `85-100`：面试前必须看；
- `70-84`：高优先级；
- `50-69`：重要辅助上下文；
- `<50`：通常只作为背景。

每个文件都会给出评分拆解和推荐理由，不是单纯输出一个数字。

### 5. 自动生成 `project_profile.md`

静态分析完成后，可以自动生成项目档案：

```text
.repo_to_interview/
├── analysis.json
└── project_profile.md
```

其中：

- `analysis.json`：结构化静态分析结果；
- `project_profile.md`：用于后续简历包装和面试准备的项目档案。

自动填充内容包括：

- 仓库概况；
- 语言与文件统计；
- 架构候选；
- Import Graph 核心节点；
- Call Graph 摘要；
- Agent 代表性执行链；
- 技术特征清单；
- 面试价值文件排名；
- 面试前源码复习清单；
- 静态分析限制。

之后 Agent 再基于高价值源码做二次阅读，补充：

- 项目整体介绍；
- Agent Engineer / LLM Application / AI Full-stack / Backend 不同岗位视角；
- 简历 bullet；
- 30 秒 / 2 分钟项目介绍；
- STAR；
- 面试追问；
- 设计取舍和失败场景。

## 关于“个人贡献”的默认策略

这个 Skill 默认用于 **用户真实参与研发的团队项目**。

因此默认：

- 不自动跑 `git blame` 判断“这段是谁写的”；
- 不要求逐个模块做 OWNED / CONTRIBUTED 分类；
- 不试图精确切割复杂团队研发边界；
- 可以把仓库中的机制作为用户参与项目的技术内容进行分析和面试准备。

但仍然避免无依据强化成：

- “我独立设计了整个系统”；
- “我主导了所有模块”；
- “所有代码均由我实现”。

更推荐团队项目中的自然表述，例如：

- 参与设计与实现……
- 负责 / 参与……模块研发；
- 项目中采用……机制；
- 围绕……进行了实现与优化。

如果用户明确知道某个模块是自己主要负责的，再进一步强化表述即可。

## 使用方法

### 1. 对目标项目执行分析

在 Skill 仓库中运行：

```bash
python scripts/analyze_repo.py /path/to/project
```

例如：

```bash
python scripts/analyze_repo.py D:/workspace/my-agent-project
```

分析结果会生成到目标项目：

```text
/path/to/project/.repo_to_interview/analysis.json
```

### 2. 自动生成项目档案

```bash
python scripts/generate_project_profile.py /path/to/project
```

生成：

```text
/path/to/project/.repo_to_interview/project_profile.md
```

### 3. 让 Agent 继续分析

推荐直接对 Codex / Claude Code / 其他 Skill-compatible Agent 说：

```text
使用 repo-to-interview 分析当前项目，目标岗位是 Agent Engineer。
先读取 .repo_to_interview/analysis.json，重点检查面试价值排名最高的源码和 Agent execution chains，
然后完善 project_profile.md。
```

或者：

```text
找出这个项目面试前最值得重新阅读的 10 个文件和函数，
说明每个位置对应什么技术机制、可能被面试官怎么追问。
```

## TypeScript 支持

TS / TSX 分析依赖 `typescript` 包。

Skill 会按顺序尝试：

1. 目标项目自身的 `node_modules/typescript`；
2. Skill 本身的 `node_modules/typescript`；
3. 当前 Node 环境可解析的全局 / 上层 `typescript`。

如果目标项目本身就是 TypeScript 项目，通常已经具备依赖。

如果没有，可以在 Skill 目录安装：

```bash
npm install typescript
```

TypeScript AST 不可用时，Python 分析仍会继续执行，并明确标记 TS 分析不可用。

## 仓库结构

```text
repo-to-interview-skill/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── LICENSE
├── references/
│   ├── confidentiality.md
│   ├── ownership-model.md
│   └── packaging-framework.md
├── templates/
│   ├── project_profile.md
│   └── review_checklist.md
├── examples/
│   └── example_project_profile.md
└── scripts/
    ├── analyze_repo.py
    ├── ts_ast_analyzer.cjs
    ├── generate_project_profile.py
    └── repo_inventory.py
```

## 公司内部项目的推荐用法

如果目标代码库属于公司内部项目，推荐直接在公司允许的开发环境中运行 Skill。

流程：

```text
公司内部代码库
  ↓
本地运行静态分析
  ↓
Agent 阅读高价值代码
  ↓
生成 project_profile.md
  ↓
脱敏
  ↓
仅保留可公开的技术描述和面试笔记
```

不要把以下内容直接带出公司环境：

- 非公开源代码；
- Secret / Token / Password；
- 内部域名、IP、接口地址；
- 客户名称或客户数据；
- 内部基础设施拓扑；
- 明确受限制的内部项目名称和业务细节。

不确定能否公开时，Skill 会建议抽象化，并标记：

```text
[REVIEW_CONFIDENTIALITY]
```

## 面向岗位的包装方向

### Agent Engineer

重点：

- Agent orchestration；
- Tool Calling；
- Agent state；
- workflow；
- evaluation；
- tracing；
- reliability；
- context / prompt；
- model routing；
- failure handling。

### LLM Application Engineer

重点：

- Prompt / Context；
- Model Integration；
- Structured Output；
- Evaluation；
- Guardrail；
- Latency / Cost；
- Observability。

### AI Full-stack Engineer

重点：

- Agent / LLM 后端集成；
- API；
- Session Persistence；
- Streaming；
- Frontend Interaction；
- Schema Contract；
- Deployment / Debugging。

### Backend Engineer

重点：

- API / Service 边界；
- Data Model；
- Async；
- Retry / Reliability；
- Observability；
- Test；
- Deployment。

## 当前限制

这是一个静态分析优先的 Skill，因此存在天然限制：

- 依赖注入可能导致调用链缺失；
- 动态 Tool Registry 无法总是准确解析；
- 反射 / monkey patch / runtime dispatch 难以静态确定；
- framework decorator 可能隐藏真实调用关系；
- 前后端跨 HTTP 的调用不会天然形成同一张函数调用图；
- 静态分析无法知道真实线上调用频率。

因此正确流程不是：

```text
AST → 直接写简历
```

而是：

```text
AST / Graph
  ↓
找出高价值候选
  ↓
Agent 定向阅读源码
  ↓
验证真实机制
  ↓
生成项目档案和面试材料
```

## License

MIT，见 [LICENSE](LICENSE)。
