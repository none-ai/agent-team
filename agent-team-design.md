# OpenAgent Agent Team 集群架构设计

## 核心理念
采用 agent team 集群方式，激活多代理协作编程，更好地完成大项目。

## 代理角色定义

### 1. 项目管理器 (ProjectManager)
- 职责：任务分解、进度跟踪、结果汇总
- 技能：任务规划、资源调度

### 2. 架构师 (Architect)
- 职责：系统设计、技术选型、代码审查
- 技能：架构设计、代码质量把控

### 3. 开发者 (Developer)
- 职责：代码实现、功能开发
- 技能：多语言编程、调试能力

### 4. 测试工程师 (QA Engineer)
- 职责：测试用例、缺陷发现
- 技能：自动化测试、质量保障

### 5. 文档工程师 (TechWriter)
- 职责：文档编写、API文档
- 技能：技术写作、知识整理

## 协作模式

### 模式一：顺序协作
```
PM → Architect → Developer → QA → TechWriter
```

### 模式二：并行协作
```
         ┌─ Developer A (前端)
PM ──────┼─ Developer B (后端)
         └─ Developer C (测试)
```

### 模式三：分层协作
```
         ┌─ SubTeam A (功能模块1)
PM ──────┼─ SubTeam B (功能模块2)
         └─ SubTeam C (集成测试)
```

## 技术实现

### 1. Agent Team 配置
```yaml
agent_teams:
  openagent_dev:
    name: "OpenAgent开发团队"
    agents:
      - role: ProjectManager
        name: "项目经理"
        model: "minimax-cn/MiniMax-M2.5-highspeed"
      - role: Architect
        name: "架构师"  
        model: "minimax-cn/MiniMax-M2.5-highspeed"
      - role: Developer
        name: "开发者A"
        model: "claude-sonnet-4-20250514"
      - role: Developer
        name: "开发者B"
        model: "claude-sonnet-4-20250514"
      - role: QA
        name: "测试工程师"
        model: "minimax-cn/MiniMax-M2.5-highspeed"
```

### 2. 任务分发协议
- 任务描述 → 自动分解 → 分发给相应角色代理
- 结果收集 → 汇总整合 → 输出最终成果

### 3. 与现有系统集成
- 利用现有的 parallel_tasks.py 管理子任务
- 利用 subagents 工具启动子代理
- 利用看板系统跟踪进度

## 使用示例

```bash
# 创建 agent team 项目
python3 scripts/agent_team.py create "OpenAgent框架开发"

# 分发任务给团队
python3 scripts/agent_team.py dispatch JJC-xxx --team openagent_dev

# 查看团队状态
python3 scripts/agent_team.py status JJC-xxx
```

---
中书省 · Agent Team 集群设计方案
日期：2026-03-09
