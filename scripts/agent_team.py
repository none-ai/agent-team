#!/usr/bin/env python3
"""
Agent Team 集群管理工具
支持创建多代理协作团队、分发任务、汇总结果

Usage:
  # 创建 agent team 项目
  python3 agent_team.py create "OpenAgent框架开发" --team openagent_dev

  # 为团队添加成员
  python3 agent_team.py add-member "开发者A" Developer --team openagent_dev

  # 分发任务给团队
  python3 agent_team.py dispatch JJC-xxx --task "实现用户认证模块"

  # 查看团队状态
  python3 agent_team.py status --team openagent_dev

  # 启动团队协作
  python3 agent_team.py start JJC-xxx --mode parallel
"""
import json
import pathlib
import sys
import argparse
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加父目录到路径
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kanban_update import load, save, find_task, now_iso

_BASE = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = _BASE / 'data'
TEAMS_FILE = DATA_DIR / 'agent_teams.json'


# 默认团队配置
DEFAULT_TEAMS = {
    "openagent_dev": {
        "name": "OpenAgent开发团队",
        "description": "用于OpenAgent项目开发的多代理协作团队",
        "members": [
            {
                "id": "pm_001",
                "name": "项目经理",
                "role": "ProjectManager",
                "description": "负责任务分解、进度跟踪、结果汇总",
                "model": "minimax-cn/MiniMax-M2.5-highspeed"
            },
            {
                "id": "arch_001",
                "name": "架构师",
                "role": "Architect",
                "description": "负责系统设计、技术选型、代码审查",
                "model": "minimax-cn/MiniMax-M2.5-highspeed"
            },
            {
                "id": "dev_001",
                "name": "开发者A",
                "role": "Developer",
                "description": "负责代码实现、功能开发",
                "model": "minimax-cn/MiniMax-M2.5-highspeed"
            },
            {
                "id": "dev_002",
                "name": "开发者B",
                "role": "Developer",
                "description": "负责代码实现、功能开发",
                "model": "minimax-cn/MiniMax-M2.5-highspeed"
            },
            {
                "id": "qa_001",
                "name": "测试工程师",
                "role": "QA",
                "description": "负责测试用例、缺陷发现",
                "model": "minimax-cn/MiniMax-M2.5-highspeed"
            }
        ]
    }
}


def load_teams() -> Dict:
    """加载团队配置"""
    if not TEAMS_FILE.exists():
        # 创建默认配置
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        save_teams(DEFAULT_TEAMS)
        return DEFAULT_TEAMS
    
    with open(TEAMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_teams(teams: Dict):
    """保存团队配置"""
    with open(TEAMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)


def create_team(team_id: str, name: str, description: str = "") -> str:
    """创建新的 agent team"""
    teams = load_teams()
    
    if team_id in teams:
        print(f"❌ 团队 {team_id} 已存在")
        return ""
    
    teams[team_id] = {
        "name": name,
        "description": description,
        "members": [],
        "created_at": now_iso()
    }
    
    save_teams(teams)
    print(f"✅ 已创建团队 {team_id}: {name}")
    return team_id


def add_member(team_id: str, name: str, role: str, description: str = "", model: str = "minimax-cn/MiniMax-M2.5-highspeed") -> str:
    """为团队添加成员"""
    teams = load_teams()
    
    if team_id not in teams:
        print(f"❌ 团队 {team_id} 不存在")
        return ""
    
    member_id = f"{role.lower()}_{len(teams[team_id]['members']) + 1:03d}"
    member = {
        "id": member_id,
        "name": name,
        "role": role,
        "description": description,
        "model": model
    }
    
    teams[team_id]["members"].append(member)
    save_teams(teams)
    
    print(f"✅ 已添加成员 {name}({role}) 到团队 {team_id}")
    return member_id


def list_teams():
    """列出所有团队"""
    teams = load_teams()
    
    print(f"\n🤖 Agent Teams ({len(teams)}个):\n")
    for team_id, team in teams.items():
        print(f"  {team_id}: {team['name']}")
        if team.get('description'):
            print(f"    描述: {team['description']}")
        print(f"    成员数: {len(team.get('members', []))}")
        for member in team.get('members', []):
            print(f"      - {member['name']}({member['role']}): {member.get('description', '')}")
        print()


def create_agent_task(parent_id: str, team_id: str, task_description: str, mode: str = "parallel") -> List[str]:
    """为 agent team 创建协作任务"""
    teams = load_teams()
    
    if team_id not in teams:
        print(f"❌ 团队 {team_id} 不存在")
        return []
    
    team = teams[team_id]
    tasks = load()
    
    # 创建父任务（团队任务）
    team_task = {
        "id": parent_id,
        "title": f"[Agent Team] {task_description}",
        "official": "中书省",
        "org": "AgentTeam",
        "state": "Doing",
        "now": f"Agent Team 协作中: {team['name']}",
        "eta": "-",
        "block": "无",
        "output": "",
        "ac": "",
        "is_agent_team": True,
        "team_id": team_id,
        "team_name": team['name'],
        "mode": mode,  # parallel 或 sequential
        "members": [],
        "flow_log": [
            {
                "at": now_iso(),
                "from": "中书省",
                "to": "AgentTeam",
                "remark": f"创建 Agent Team 任务: {team['name']}"
            }
        ],
        "updatedAt": now_iso(),
        "todos": [],
        "progress_log": []
    }
    
    # 为每个成员创建子任务
    sub_task_ids = []
    for i, member in enumerate(team.get('members', [])):
        sub_id = f"{parent_id}-M{i+1:02d}"
        sub_task_ids.append(sub_id)
        
        sub_task = {
            "id": sub_id,
            "title": f"[{task_description}] {member['name']}({member['role']})",
            "official": "中书省",
            "org": "AgentTeam",
            "state": "Assigned",
            "now": f"等待 {member['name']} 执行",
            "eta": "-",
            "block": "无",
            "output": "",
            "ac": "",
            "parent_id": parent_id,
            "is_agent_member_task": True,
            "team_id": team_id,
            "member_id": member['id'],
            "member_name": member['name'],
            "member_role": member['role'],
            "member_model": member.get('model', 'minimax-cn/MiniMax-M2.5-highspeed'),
            "flow_log": [
                {
                    "at": now_iso(),
                    "from": "AgentTeam",
                    "to": member['name'],
                    "remark": f"分配任务给 {member['role']}"
                }
            ],
            "updatedAt": now_iso(),
            "todos": [
                {
                    "id": "1",
                    "title": f"{member['role']} 任务",
                    "status": "pending"
                }
            ],
            "progress_log": []
        }
        
        team_task["todos"].append({
            "id": str(i + 1),
            "title": f"{member['name']}({member['role']})",
            "status": "pending",
            "member_id": member['id']
        })
        
        tasks.append(sub_task)
    
    tasks.append(team_task)
    save(tasks)
    
    print(f"✅ 已创建 Agent Team 任务 {parent_id}")
    print(f"   团队: {team['name']}")
    print(f"   模式: {mode}")
    print(f"   成员任务数: {len(sub_task_ids)}")
    
    return sub_task_ids


def status(team_id: str = None, task_id: str = None):
    """查看团队或任务状态"""
    if task_id:
        tasks = load()
        task = find_task(tasks, task_id)
        
        if not task:
            print(f"❌ 任务 {task_id} 不存在")
            return
        
        print(f"\n📋 Agent Team 任务状态: {task_id}")
        print(f"   标题: {task.get('title', '')}")
        print(f"   团队: {task.get('team_name', 'N/A')}")
        print(f"   模式: {task.get('mode', 'N/A')}")
        print(f"   状态: {task.get('state', 'N/A')}")
        
        # 显示成员任务状态
        subs = [t for t in tasks if t.get('parent_id') == task_id and t.get('is_agent_member_task')]
        print(f"\n   成员任务 ({len(subs)}个):")
        for sub in subs:
            status_icon = "✅" if sub.get('state') == 'Done' else "🔄" if sub.get('state') in ('Doing', 'Assigned') else "⏳"
            print(f"      {status_icon} {sub['member_name']}({sub['member_role']}): {sub.get('state', 'N/A')}")
        print()
        
    elif team_id:
        teams = load_teams()
        if team_id not in teams:
            print(f"❌ 团队 {team_id} 不存在")
            return
        
        team = teams[team_id]
        print(f"\n🤖 团队: {team['name']}")
        print(f"   描述: {team.get('description', 'N/A')}")
        print(f"   成员数: {len(team.get('members', []))}")
        
        for member in team.get('members', []):
            print(f"\n   成员: {member['name']}")
            print(f"      角色: {member['role']}")
            print(f"      模型: {member.get('model', 'N/A')}")
            print(f"      描述: {member.get('description', '')}")
        print()
    else:
        list_teams()


def dispatch_task(task_id: str):
    """分发任务给团队成员（启动子代理）"""
    tasks = load()
    task = find_task(tasks, task_id)
    
    if not task:
        print(f"❌ 任务 {task_id} 不存在")
        return
    
    if not task.get('is_agent_team'):
        print(f"❌ 任务 {task_id} 不是 Agent Team 任务")
        return
    
    subs = [t for t in tasks if t.get('parent_id') == task_id and t.get('is_agent_member_task')]
    
    print(f"🚀 正在启动 {len(subs)} 个子代理...")
    
    for sub in subs:
        if sub.get('state') == 'Done':
            continue
        
        # 更新状态
        sub['state'] = 'Doing'
        sub['now'] = f"子代理 {sub['member_name']} 执行中"
        sub['updatedAt'] = now_iso()
        
        # TODO: 实际启动 subagent 的逻辑
        # 使用 subagents 工具启动子代理
        print(f"   ✅ 启动 {sub['member_name']}({sub['member_role']})")
    
    # 更新父任务状态
    task['state'] = 'Doing'
    task['now'] = f"Agent Team 协作执行中"
    task['updatedAt'] = now_iso()
    
    save(tasks)
    print(f"\n✅ 已启动 {len(subs)} 个子代理执行任务")


def main():
    parser = argparse.ArgumentParser(description='Agent Team 集群管理工具')
    subparsers = parser.add_subparsers(dest='cmd', help='子命令')
    
    # create
    parser_create = subparsers.add_parser('create', help='创建 agent team')
    parser_create.add_argument('name', help='团队名称')
    parser_create.add_argument('--id', dest='team_id', help='团队ID')
    parser_create.add_argument('--desc', dest='description', default='', help='团队描述')
    
    # add-member
    parser_add = subparsers.add_parser('add-member', help='添加团队成员')
    parser_add.add_argument('name', help='成员名称')
    parser_add.add_argument('role', help='角色(PM/Architect/Developer/QA/TechWriter)')
    parser_add.add_argument('--team', required=True, help='团队ID')
    parser_add.add_argument('--desc', dest='description', default='', help='成员描述')
    parser_add.add_argument('--model', default='minimax-cn/MiniMax-M2.5-highspeed', help='使用模型')
    
    # list
    subparsers.add_parser('list', help='列出所有团队')
    
    # dispatch
    parser_dispatch = subparsers.add_parser('dispatch', help='创建并分发团队任务')
    parser_dispatch.add_argument('task_id', help='父任务ID')
    parser_dispatch.add_argument('--team', required=True, help='团队ID')
    parser_dispatch.add_argument('--task', required=True, help='任务描述')
    parser_dispatch.add_argument('--mode', default='parallel', choices=['parallel', 'sequential'], help='协作模式')
    
    # status
    parser_status = subparsers.add_parser('status', help='查看团队/任务状态')
    parser_status.add_argument('--team', help='团队ID')
    parser_status.add_argument('--task', dest='task_id', help='任务ID')
    
    # start
    parser_start = subparsers.add_parser('start', help='启动团队协作')
    parser_start.add_argument('task_id', help='任务ID')
    
    args = parser.parse_args()
    
    if args.cmd == 'create':
        team_id = args.team_id or f"team_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        create_team(team_id, args.name, args.description)
    elif args.cmd == 'add-member':
        add_member(args.team, args.name, args.role, args.description, args.model)
    elif args.cmd == 'list':
        list_teams()
    elif args.cmd == 'dispatch':
        create_agent_task(args.task_id, args.team, args.task, args.mode)
    elif args.cmd == 'status':
        status(args.team, args.task_id)
    elif args.cmd == 'start':
        dispatch_task(args.task_id)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
