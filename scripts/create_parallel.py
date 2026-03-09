#!/usr/bin/env python3
"""
批量并行任务创建器 - 中书省专用
用于快速创建可并行执行的多个子任务

Usage:
  python3 create_parallel.py "任务标题" "子任务1,子任务2,子任务3" 中书省
  python3 create_parallel.py "开发项目" "前端,后端,测试,部署" 尚书省
"""
import sys
import pathlib
import datetime
from typing import List

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kanban_update import load, save, now_iso

TASKS_FILE = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'tasks_source.json'


def generate_task_id(prefix="JJC") -> str:
    """生成任务ID"""
    today = datetime.datetime.now().strftime("%Y%m%d")
    tasks = load()
    today_tasks = [t for t in tasks if t['id'].startswith(f"{prefix}-{today}")]
    
    if today_tasks:
        max_num = max(int(t['id'].split('-')[-1]) for t in today_tasks)
        new_num = max_num + 1
    else:
        new_num = 1
    
    return f"{prefix}-{today}-{new_num:03d}"


def create_parallel_tasks(title: str, sub_titles: List[str], org: str = "中书省", description: str = "") -> str:
    """
    创建并行任务组
    返回父任务ID
    """
    tasks = load()
    parent_id = generate_task_id()
    
    # 创建父任务（任务组）
    parent_task = {
        "id": parent_id,
        "title": title,
        "official": "太子",
        "org": org,
        "state": org,
        "now": f"并行任务组：{len(sub_titles)}个子任务",
        "eta": "-",
        "block": "无",
        "output": "",
        "ac": "",
        "is_parallel_group": True,
        "is_batch": True,
        "parallel_subs": [],
        "description": description,
        "flow_log": [
            {
                "at": now_iso(),
                "from": "太子",
                "to": org,
                "remark": f"创建并行任务组，包含{len(sub_titles)}个可并行子任务"
            }
        ],
        "updatedAt": now_iso(),
        "todos": [],
        "progress_log": []
    }
    
    # 创建子任务
    for i, sub_title in enumerate(sub_titles):
        sub_id = f"{parent_id}-P{i+1:02d}"
        parent_task["parallel_subs"].append(sub_id)
        
        sub_task = {
            "id": sub_id,
            "title": f"[{title}] {sub_title}",
            "official": "太子",
            "org": org,
            "state": org,
            "now": "等待并行执行",
            "eta": "-",
            "block": "无",
            "output": "",
            "ac": "",
            "parent_id": parent_id,
            "parent_title": title,
            "is_parallel_child": True,
            "parallel_index": i,
            "parallel_group_size": len(sub_titles),
            "flow_log": [
                {
                    "at": now_iso(),
                    "from": "太子",
                    "to": org,
                    "remark": f"创建并行子任务 {i+1}/{len(sub_titles)}"
                }
            ],
            "updatedAt": now_iso(),
            "todos": [
                {
                    "id": "1",
                    "title": sub_title,
                    "status": "pending",
                    "is_parallel": True
                }
            ],
            "progress_log": []
        }
        
        # 添加到父任务的todos
        parent_task["todos"].append({
            "id": str(i + 1),
            "title": sub_title,
            "status": "pending",
            "is_parallel": True
        })
        
        tasks.append(sub_task)
    
    tasks.append(parent_task)
    save(tasks)
    
    return parent_id


def create_parallel_tasks_auto(title: str, sub_titles: List[str], org: str = "中书省") -> dict:
    """
    自动创建并行任务（带自动调度）
    """
    parent_id = create_parallel_tasks(title, sub_titles, org)
    
    return {
        "parent_id": parent_id,
        "sub_count": len(sub_titles),
        "sub_ids": [f"{parent_id}-P{i+1:02d}" for i in range(len(sub_titles))],
        "message": f"✅ 已创建并行任务组 {parent_id}，包含 {len(sub_titles)} 个子任务"
    }


# 命令行入口
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='批量创建并行任务')
    parser.add_argument('title', help='任务标题')
    parser.add_argument('sub_titles', help='子任务标题（逗号分隔）')
    parser.add_argument('org', nargs='?', default='中书省', help='负责部门')
    parser.add_argument('--desc', default='', help='任务描述')
    
    args = parser.parse_args()
    
    sub_titles = [s.strip() for s in args.sub_titles.split(',')]
    result = create_parallel_tasks(args.title, sub_titles, args.org, args.desc)
    
    print(f"\n✅ 并行任务组已创建:")
    print(f"   父任务: {result}")
    print(f"   子任务数: {len(sub_titles)}")
    for i, sub in enumerate(sub_titles):
        print(f"   - {result}-P{i+1:02d}: {sub}")
