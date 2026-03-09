# Agent Team Cluster - 多代理协作系统

> 基于 OpenClaw 的多代理协作编程框架，激活 Agent 集群编程能力

## 概述

Agent Team Cluster 是一个多代理协作系统，采用 agent team 集群方式，激活多代理协作编程，更好地完成大项目。

## 核心特性

- **多角色代理**：支持项目经理、架构师、开发者、测试工程师、文档工程师等多种角色
- **多种协作模式**：顺序协作、并行协作、分层协作
- **任务管理**：支持任务分解、状态追踪、结果汇总
- **与 OpenClaw 集成**：无缝对接 OpenClaw 看板系统和子代理机制

## 架构设计

### 代理角色

| 角色 | 职责 | 技能 |
|------|------|------|
| 项目管理器 | 任务分解、进度跟踪、结果汇总 | 任务规划、资源调度 |
| 架构师 | 系统设计、技术选型、代码审查 | 架构设计、质量把控 |
| 开发者 | 代码实现、功能开发 | 多语言编程、调试 |
| 测试工程师 | 测试用例、缺陷发现 | 自动化测试、质量保障 |
| 文档工程师 | 文档编写、API文档 | 技术写作、知识整理 |

### 协作模式

#### 模式一：顺序协作
```
PM → Architect → Developer → QA → TechWriter
```

#### 模式二：并行协作
```
         ┌─ Developer A (前端)
PM ──────┼─ Developer B (后端)
         └─ Developer C (测试)
```

#### 模式三：分层协作
```
         ┌─ SubTeam A (功能模块1)
PM ──────┼─ SubTeam B (功能模块2)
         └─ SubTeam C (集成测试)
```

## 快速开始

### 环境要求

- Python 3.8+
- OpenClaw

### 安装

```bash
# 克隆项目
git clone https://github.com/none-ai/agent-team.git
cd agent-team
```

### 使用

```bash
# 创建 agent team 项目
python3 scripts/agent_team.py create "新项目开发"

# 分发任务给团队
python3 scripts/agent_team.py dispatch JJC-xxx --team openagent_dev

# 查看团队状态
python3 scripts/agent_team.py status JJC-xxx
```

## 项目结构

```
agent-team/
├── scripts/
│   ├── agent_team.py        # Agent Team 核心工具
│   ├── create_parallel.py  # 批量创建并行任务
│   ├── parallel_tasks.py   # 并行任务管理
│   └── parallel_scheduler.py # 并行任务调度器
├── memory/
│   ├── agent-team-design.md    # 架构设计文档
│   └── agent-team.md          # 执行记录
├── PARALLEL_WORKFLOW.md    # 并行工作流文档
└── README.md               # 本文档
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---

**作者**: Agent Team Cluster  
**维护**: 中书省  
**版本**: 1.0.0
