#!/usr/bin/env python3
"""
并行任务调度器 - 中书省自动化并行处理
自动检测可并行任务，调度子代理并行执行

功能：
1. 自动扫描待执行的并行任务
2. 智能分配子代理资源
3. 监控并行任务执行状态
4. 任务完成后自动汇总

Usage:
  python3 parallel_scheduler.py scan          # 扫描可并行任务
  python3 parallel_scheduler.py dispatch      # 调度执行
  python3 parallel_scheduler.py status        # 查看并行任务状态
  python3 parallel_scheduler.py daemon        # 后台持续运行
"""
import json
import pathlib
import sys
import time
import subprocess
import argparse
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from kanban_update import load, save, find_task, now_iso

_BASE = pathlib.Path(__file__).resolve().parent.parent
TASKS_FILE = _BASE / 'data' / 'tasks_source.json'

# 可用代理配置
AVAILABLE_AGENTS = {
    'zhongshu': '中书省',
    'menxia': '门下省', 
    'shangshu': '尚书省',
    'libu': '礼部',
    'hubu': '户部',
    'bingbu': '兵部',
    'xingbu': '刑部',
    'gongbu': '工部',
}


def get_parallel_tasks():
    """获取所有可并行执行的任务"""
    tasks = load()
    
    # 找出并行任务组（状态不是 Done）
    parallel_groups = [t for t in tasks if t.get('is_parallel_group') and t.get('state') != 'Done']
    
    # 状态映射
    pending_states = ['Zhongshu', '中书省', 'Pending', 'Assigned', 'Doing', 'Doing']
    
    result = []
    for group in parallel_groups:
        subs = [t for t in tasks if t.get('parent_id') == group['id']]
        
        # 统计待执行的子任务
        pending_subs = [s for s in subs if s.get('state') in pending_states and s.get('state') != 'Done']
        
        if pending_subs:
            result.append({
                'group': group,
                'pending': pending_subs,
                'total': len(subs),
                'completed': len(subs) - len(pending_subs)
            })
    
    return result


def dispatch_parallel_task(group_id: str, max_parallel: int = 3):
    """调度并行任务执行"""
    tasks = load()
    group = find_task(tasks, group_id)
    
    if not group:
        print(f"❌ 任务组 {group_id} 不存在")
        return
    
    subs = [t for t in tasks if t.get('parent_id') == group_id and t.get('state') != 'Done']
    
    # 限制并行数量
    to_dispatch = subs[:max_parallel]
    
    print(f"🚀 调度 {len(to_dispatch)} 个子任务并行执行...")
    
    # 这里可以启动多个子代理并行执行
    # 当前使用 subprocess 模拟，实际应该调用 subagents 工具
    
    results = []
    with ThreadPoolExecutor(max_workers=len(to_dispatch)) as executor:
        futures = {executor.submit(execute_sub_task, sub): sub for sub in to_dispatch}
        
        for future in as_completed(futures):
            sub = futures[future]
            try:
                result = future.result()
                results.append((sub['id'], result))
                print(f"  ✅ {sub['id']} 完成")
            except Exception as e:
                print(f"  ❌ {sub['id']} 失败: {e}")
    
    return results


def execute_sub_task(sub_task):
    """执行单个子任务（可被并行调用）"""
    # 模拟任务执行
    # 实际这里应该调用具体的处理函数或启动子代理
    time.sleep(0.5)  # 模拟执行时间
    
    return {
        'status': 'completed',
        'output': f"子任务 {sub_task['id']} 执行完成"
    }


def scan_and_report():
    """扫描并行任务并生成报告"""
    parallel_tasks = get_parallel_tasks()
    
    if not parallel_tasks:
        print("📋 当前没有待执行的并行任务")
        return
    
    print(f"\n📊 并行任务扫描报告 ({len(parallel_tasks)}个任务组)\n")
    print("=" * 60)
    
    for item in parallel_tasks:
        group = item['group']
        progress = f"{item['completed']}/{item['total']}"
        pct = (item['completed'] / item['total'] * 100) if item['total'] > 0 else 0
        
        print(f"\n📁 {group['id']}: {group['title']}")
        print(f"   进度: {progress} ({pct:.0f}%)")
        print(f"   等待执行: {len(item['pending'])}个")
        
        for sub in item['pending'][:3]:  # 只显示前3个
            print(f"   ⏳ {sub['id']}: {sub['title'][:40]}")
        if len(item['pending']) > 3:
            print(f"   ... 还有 {len(item['pending']) - 3} 个")
    
    print("\n" + "=" * 60)
    
    total_pending = sum(len(item['pending']) for item in parallel_tasks)
    print(f"\n📈 总计: {len(parallel_tasks)} 个任务组, {total_pending} 个子任务待执行")


def auto_dispatch_all(max_parallel_per_group: int = 3, max_total: int = 10):
    """自动调度所有可并行任务"""
    parallel_tasks = get_parallel_tasks()
    
    if not parallel_tasks:
        print("没有可调度的并行任务")
        return
    
    dispatched = 0
    for item in parallel_tasks:
        if dispatched >= max_total:
            break
            
        group = item['group']
        subs_to_do = min(len(item['pending']), max_parallel_per_group)
        
        print(f"\n处理任务组: {group['id']}")
        dispatch_parallel_task(group['id'], subs_to_do)
        
        dispatched += subs_to_do
    
    print(f"\n✅ 已调度 {dispatched} 个子任务并行执行")


def run_daemon(interval: int = 300):
    """后台持续运行，自动调度并行任务"""
    print(f"🔄 并行调度器已启动，每 {interval} 秒检查一次...")
    print("按 Ctrl+C 停止\n")
    
    while True:
        try:
            parallel_tasks = get_parallel_tasks()
            
            if parallel_tasks:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 发现 {len(parallel_tasks)} 个可并行任务组")
                auto_dispatch_all()
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 无新任务")
            
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 调度器已停止")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description='并行任务调度器')
    subparsers = parser.add_subparsers(dest='cmd', help='子命令')
    
    subparsers.add_parser('scan', help='扫描可并行任务')
    subparsers.add_parser('dispatch', help='调度执行')
    subparsers.add_parser('status', help='查看并行任务状态（同scan）')
    
    parser_daemon = subparsers.add_parser('daemon', help='后台持续运行')
    parser_daemon.add_argument('--interval', type=int, default=300, help='检查间隔（秒）')
    
    args = parser.parse_args()
    
    if args.cmd == 'scan' or args.cmd == 'status':
        scan_and_report()
    elif args.cmd == 'dispatch':
        auto_dispatch_all()
    elif args.cmd == 'daemon':
        run_daemon(args.interval)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
