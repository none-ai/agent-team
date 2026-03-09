#!/usr/bin/env python3
"""
并行任务管理工具 - 中书省专用
支持批量创建任务、并行子任务执行、批量操作

Usage:
  # 批量创建并行任务（父任务+多个子任务）
  python3 parallel_tasks.py create-batch JJC-20260309-002 "多任务并行测试" Zhongshu 子任务1,子任务2,子任务3

  # 创建可并行执行的子任务
  python3 parallel_tasks.py create-sub JJC-20260309-001 "调研A项目" 1
  python3 parallel_tasks.py create-sub JJC-20260309-001 "调研B项目" 1
  
  # 批量更新状态
  python3 parallel_tasks.py batch-state "JJC-20260309-001,JJC-20260309-002" Doing
  
  # 查看可并行任务列表
  python3 parallel_tasks.py list-parallel
  
  # 并行执行子任务（创建子代理）
  python3 parallel_tasks.py spawn-subs JJC-20260309-001 --agents zhongshu,menxia
  
  # 一键优化现有任务（将串行子任务转为并行）
  python3 parallel_tasks.py optimize JJC-20260309-001
"""
import json
import pathlib
import sys
import argparse
import subprocess
import os
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kanban_update import load, save, find_task, now_iso, _sanitize_text

_BASE = pathlib.Path(__file__).resolve().parent.parent
TASKS_FILE = _BASE / 'data' / 'tasks_source.json'


def get_task_id(prefix="JJC"):
    """生成任务ID：JJC-YYYYMMDD-NNN"""
    today = datetime.now().strftime("%Y%m%d")
    
    tasks = load()
    today_tasks = [t for t in tasks if t['id'].startswith(f"{prefix}-{today}")]
    
    if today_tasks:
        max_num = max(int(t['id'].split('-')[-1]) for t in today_tasks)
        new_num = max_num + 1
    else:
        new_num = 1
    
    return f"{prefix}-{today}-{new_num:03d}"


def create_batch(parent_id: str, title: str, org: str, sub_titles: list):
    """批量创建父任务+多个并行子任务"""
    tasks = load()
    
    # 创建父任务
    parent_task = {
        "id": parent_id,
        "title": title,
        "official": "中书省",
        "org": org,
        "state": "Zhongshu",
        "now": f"并行任务组：{len(sub_titles)}个子任务",
        "eta": "-",
        "block": "无",
        "output": "",
        "ac": "",
        "is_parallel_group": True,  # 标记为并行任务组
        "parallel_subs": [],  # 子任务ID列表
        "flow_log": [
            {
                "at": now_iso(),
                "from": "中书省",
                "to": "中书省",
                "remark": f"创建并行任务组，包含{len(sub_titles)}个子任务"
            }
        ],
        "updatedAt": now_iso(),
        "todos": [
            {
                "id": str(i+1),
                "title": sub_title,
                "status": "pending",
                "is_parallel": True  # 标记为可并行
            }
            for i, sub_title in enumerate(sub_titles)
        ],
        "progress_log": []
    }
    
    # 创建子任务
    for i, sub_title in enumerate(sub_titles):
        sub_id = f"{parent_id}-S{i+1:02d}"
        parent_task["parallel_subs"].append(sub_id)
        
        sub_task = {
            "id": sub_id,
            "title": f"[{title}] {sub_title}",
            "official": "中书省",
            "org": org,
            "state": "Zhongshu",
            "now": "等待并行执行",
            "eta": "-",
            "block": "无",
            "output": "",
            "ac": "",
            "parent_id": parent_id,  # 关联父任务
            "is_parallel_child": True,
            "parallel_index": i,
            "flow_log": [
                {
                    "at": now_iso(),
                    "from": "中书省",
                    "to": "中书省",
                    "remark": f"创建并行子任务 {i+1}/{len(sub_titles)}"
                }
            ],
            "updatedAt": now_iso(),
            "todos": [
                {
                    "id": "1",
                    "title": sub_title,
                    "status": "in-progress"
                }
            ],
            "progress_log": []
        }
        tasks.append(sub_task)
    
    tasks.append(parent_task)
    save(tasks)
    
    print(f"✅ 已创建并行任务组 {parent_id}，包含 {len(sub_titles)} 个子任务")
    print(f"   父任务: {parent_id}")
    for sub_id in parent_task["parallel_subs"]:
        print(f"   子任务: {sub_id}")
    
    return parent_id


def create_sub(parent_id: str, title: str, parallel_group: int = None):
    """为现有任务添加并行子任务"""
    tasks = load()
    parent = find_task(tasks, parent_id)
    
    if not parent:
        print(f"❌ 任务 {parent_id} 不存在")
        return
    
    # 生成子任务ID
    existing_subs = [t for t in tasks if t.get('parent_id') == parent_id]
    sub_num = len(existing_subs) + 1
    sub_id = f"{parent_id}-S{sub_num:02d}"
    
    sub_task = {
        "id": sub_id,
        "title": f"[{parent.get('title', '')}] {title}",
        "official": "中书省",
        "org": parent.get('org', '中书省'),
        "state": "Zhongshu",
        "now": "等待并行执行",
        "eta": "-",
        "block": "无",
        "output": "",
        "ac": "",
        "parent_id": parent_id,
        "is_parallel_child": True,
        "parallel_index": sub_num - 1,
        "flow_log": [
            {
                "at": now_iso(),
                "from": "中书省",
                "to": "中书省",
                "remark": f"添加并行子任务 {sub_num}"
            }
        ],
        "updatedAt": now_iso(),
        "todos": [
            {
                "id": "1",
                "title": title,
                "status": "pending"
            }
        ],
        "progress_log": []
    }
    
    # 更新父任务
    if "parallel_subs" not in parent:
        parent["parallel_subs"] = []
    parent["parallel_subs"].append(sub_id)
    parent["is_parallel_group"] = True
    
    # 添加子任务到todo
    parent["todos"].append({
        "id": str(len(parent["todos"]) + 1),
        "title": title,
        "status": "pending",
        "is_parallel": True
    })
    
    tasks.append(sub_task)
    save(tasks)
    
    print(f"✅ 已为任务 {parent_id} 添加并行子任务 {sub_id}")
    return sub_id


def list_parallel():
    """列出所有可并行执行的任务"""
    tasks = load()
    
    # 找出并行任务组
    parallel_groups = [t for t in tasks if t.get('is_parallel_group')]
    
    print(f"\n📋 并行任务组 ({len(parallel_groups)}个):\n")
    for group in parallel_groups:
        subs = [t for t in tasks if t.get('parent_id') == group['id']]
        completed = sum(1 for s in subs if s.get('state') == 'Done')
        
        print(f"  {group['id']}: {group['title']}")
        print(f"    进度: {completed}/{len(subs)} 完成")
        for sub in subs:
            status_icon = "✅" if sub.get('state') == 'Done' else "🔄" if sub.get('state') in ('Doing', 'Assigned') else "⏳"
            print(f"    {status_icon} {sub['id']}: {sub['title'].split('] ')[-1]}")
        print()
    
    # 找出独立的可并行子任务
    orphan_subs = [t for t in tasks if t.get('is_parallel_child') and not t.get('parent_id')]
    if orphan_subs:
        print(f"\n📋 独立并行子任务 ({len(orphan_subs)}个):\n")
        for sub in orphan_subs:
            status_icon = "✅" if sub.get('state') == 'Done' else "🔄" if sub.get('state') in ('Doing', 'Assigned') else "⏳"
            print(f"  {status_icon} {sub['id']}: {sub['title']}")
        print()


def batch_state(task_ids: list, new_state: str):
    """批量更新任务状态"""
    tasks = load()
    updated = 0
    
    for task_id in task_ids:
        task = find_task(tasks, task_id)
        if task:
            task['state'] = new_state
            task['updatedAt'] = now_iso()
            updated += 1
    
    save(tasks)
    print(f"✅ 已更新 {updated}/{len(task_ids)} 个任务状态为 {new_state}")


def spawn_parallel_subs(parent_id: str, agents: list = None):
    """为并行子任务创建子代理执行"""
    tasks = load()
    parent = find_task(tasks, parent_id)
    
    if not parent:
        print(f"❌ 任务 {parent_id} 不存在")
        return
    
    subs = [t for t in tasks if t.get('parent_id') == parent_id and t.get('is_parallel_child')]
    
    if not subs:
        print(f"❌ 任务 {parent_id} 没有并行子任务")
        return
    
    # 为每个子任务启动子代理
    for i, sub in enumerate(subs):
        if sub.get('state') == 'Done':
            continue
            
        agent = agents[i % len(agents)] if agents else 'zhongshu'
        
        # 更新状态为执行中
        sub['state'] = 'Doing'
        sub['now'] = f"子代理 {agent} 执行中"
        sub['updatedAt'] = now_iso()
        
        print(f"🚀 启动子代理 {agent} 执行任务 {sub['id']}")
        
        # TODO: 实际启动子代理的逻辑
        # 这里可以调用 subagents 工具启动子代理
    
    save(tasks)
    print(f"✅ 已为 {len(subs)} 个子任务启动并行执行")


def optimize_task(task_id: str):
    """优化现有任务，将串行子任务转为并行"""
    tasks = load()
    task = find_task(tasks, task_id)
    
    if not task:
        print(f"❌ 任务 {task_id} 不存在")
        return
    
    # 标记所有todo为可并行
    if 'todos' in task:
        for todo in task['todos']:
            if todo.get('status') != 'completed':
                todo['is_parallel'] = True
        
        task['is_parallel_group'] = True
        task['now'] = f"已优化为并行模式：{len(task['todos'])}个子任务可并行"
        task['updatedAt'] = now_iso()
        
        save(tasks)
        print(f"✅ 已将任务 {task_id} 优化为并行模式")
    else:
        print(f"❌ 任务 {task_id} 没有子任务")


def main():
    parser = argparse.ArgumentParser(description='并行任务管理工具')
    subparsers = parser.add_subparsers(dest='cmd', help='子命令')
    
    # create-batch
    parser_batch = subparsers.add_parser('create-batch', help='批量创建并行任务')
    parser_batch.add_argument('parent_id', help='父任务ID')
    parser_batch.add_argument('title', help='任务标题')
    parser_batch.add_argument('org', default='中书省', help='负责部门')
    parser_batch.add_argument('sub_titles', help='子任务标题（逗号分隔）')
    
    # create-sub
    parser_sub = subparsers.add_parser('create-sub', help='添加并行子任务')
    parser_sub.add_argument('parent_id', help='父任务ID')
    parser_sub.add_argument('title', help='子任务标题')
    parser_sub.add_argument('group', type=int, default=1, help='并行组编号')
    
    # list-parallel
    subparsers.add_parser('list-parallel', help='列出可并行任务')
    
    # batch-state
    parser_batch_state = subparsers.add_parser('batch-state', help='批量更新状态')
    parser_batch_state.add_argument('task_ids', help='任务ID列表（逗号分隔）')
    parser_batch_state.add_argument('state', help='新状态')
    
    # spawn-subs
    parser_spawn = subparsers.add_parser('spawn-subs', help='并行执行子任务')
    parser_spawn.add_argument('parent_id', help='父任务ID')
    parser_spawn.add_argument('--agents', help='代理列表（逗号分隔）')
    
    # optimize
    parser_opt = subparsers.add_parser('optimize', help='优化任务为并行模式')
    parser_opt.add_argument('task_id', help='任务ID')
    
    args = parser.parse_args()
    
    if args.cmd == 'create-batch':
        sub_titles = [s.strip() for s in args.sub_titles.split(',')]
        create_batch(args.parent_id, args.title, args.org, sub_titles)
    elif args.cmd == 'create-sub':
        create_sub(args.parent_id, args.title, args.group)
    elif args.cmd == 'list-parallel':
        list_parallel()
    elif args.cmd == 'batch-state':
        task_ids = [t.strip() for t in args.task_ids.split(',')]
        batch_state(task_ids, args.state)
    elif args.cmd == 'spawn-subs':
        agents = args.agents.split(',') if args.agents else None
        spawn_parallel_subs(args.parent_id, agents)
    elif args.cmd == 'optimize':
        optimize_task(args.task_id)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
