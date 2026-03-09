# 并行任务处理指南

## 概述

为提升工作效率，中书省已建立并行任务处理机制，支持以下场景：

## 工具清单

### 1. 批量创建并行任务
```bash
# 创建包含多个子任务的并行任务组
python3 scripts/create_parallel.py "项目开发" "前端,后端,测试,部署" 尚书省
```

### 2. 并行任务管理
```bash
# 列出所有可并行任务
python3 scripts/parallel_tasks.py list-parallel

# 为现有任务添加并行子任务
python3 scripts/parallel_tasks.py create-sub JJC-20260309-001 "调研A项目" 1

# 批量更新状态
python3 scripts/parallel_tasks.py batch-state "JJC-xxx,JJC-yyy" Doing
```

### 3. 并行任务调度器
```bash
# 扫描可并行任务
python3 scripts/parallel_scheduler.py scan

# 自动调度执行
python3 scripts/parallel_scheduler.py dispatch

# 后台持续运行（每5分钟检查一次）
python3 scripts/parallel_scheduler.py daemon --interval 300
```

## 工作流程

### 场景一：太子传递多任务旨意

当太子收到旨意包含多个可独立执行的工作项时：

1. **太子使用 create_parallel.py 创建任务组**
```bash
python3 scripts/create_parallel.py "调研舆论并开发高Star项目" "迭代openhome,开发OpenAgent框架,发布到GitHub" 尚书省
```

2. **系统自动创建**：
   - 父任务：JJC-20260309-XXX（任务组）
   - 子任务：JJC-20260309-XXX-P01, P02, P03（可并行执行）

3. **尚书省收到任务后**，可使用调度器并行执行：
```bash
python3 scripts/parallel_scheduler.py dispatch
```

### 场景二：任务执行中需要并行处理

当中书省/尚书省处理任务时发现可并行的子任务：

1. **使用 parallel_tasks.py 添加并行子任务**
```bash
python3 scripts/parallel_tasks.py create-sub JJC-20260309-001 "调研A项目" 1
python3 scripts/parallel_tasks.py create-sub JJC-20260309-001 "调研B项目" 1
```

2. **使用 parallel_tasks.py 启动并行执行**
```bash
python3 scripts/parallel_tasks.py spawn-subs JJC-20260309-001 --agents zhongshu,shangshu
```

## 任务标记说明

| 标记 | 含义 |
|------|------|
| `is_parallel_group` | 任务组（父任务） |
| `is_parallel_child` | 并行子任务 |
| `parallel_index` | 子任务序号 |
| `parallel_group_size` | 任务组总子任务数 |
| `is_parallel: true` | todo中标记为可并行 |

## 并行执行规则

1. **独立性优先**：只有相互独立的任务才能并行
2. **资源控制**：默认最多同时执行3个子任务
3. **状态同步**：子任务完成后自动更新父任务进度
4. **错误隔离**：单个子任务失败不影响其他子任务

## 尚书省并行处理流程

```
收到多任务旨意
    ↓
使用 create_parallel.py 创建并行任务组
    ↓
使用 parallel_scheduler.py scan 查看待执行任务
    ↓
使用 parallel_scheduler.py dispatch 自动调度
    ↓
子任务并行执行中...
    ↓
全部完成后自动汇总结果
```

---
中书省 · 机构改革成果
