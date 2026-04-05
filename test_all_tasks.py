#!/usr/bin/env python3
"""Comprehensive test to verify all tasks can be solved correctly"""

from server.tasks.task_easy import EASY_TASKS
from server.tasks.task_medium import MEDIUM_TASKS  
from server.tasks.task_hard import HARD_TASKS
from server.graders.grader_easy import grade_easy
from server.graders.grader_medium import grade_medium
from server.graders.grader_hard import grade_hard

def test_all_easy_tasks():
    print("="*70)
    print("TESTING ALL EASY TASKS")
    print("="*70)
    failed = []
    for task in EASY_TASKS:
        task_id = task['task_id']
        try:
            reward, passed, total, feedback, _ = grade_easy(task['fixed_code'], task)
            if reward < 1.0:
                failed.append((task_id, reward, f"{passed}/{total} tests passed"))
                print(f"❌ {task_id}: reward={reward:.2f} ({passed}/{total})")
            else:
                print(f"✅ {task_id}: reward={reward:.2f} ({passed}/{total})")
        except Exception as e:
            failed.append((task_id, 0.0, str(e)))
            print(f"💥 {task_id}: ERROR - {e}")
    
    print(f"\n{'='*70}")
    print(f"EASY TASKS: {len(EASY_TASKS) - len(failed)}/{len(EASY_TASKS)} passed")
    if failed:
        print("Failed tasks:")
        for task_id, reward, reason in failed:
            print(f"  - {task_id}: {reason}")
    print("="*70)
    return len(failed) == 0

def test_all_medium_tasks():
    print("\n" + "="*70)
    print("TESTING ALL MEDIUM TASKS")
    print("="*70)
    failed = []
    for task in MEDIUM_TASKS:
        task_id = task['task_id']
        try:
            reward, passed, total, feedback, _ = grade_medium(task['fixed_code'], task)
            if reward < 1.0:
                failed.append((task_id, reward, f"{passed}/{total} tests passed"))
                print(f"❌ {task_id}: reward={reward:.2f} ({passed}/{total})")
            else:
                print(f"✅ {task_id}: reward={reward:.2f} ({passed}/{total})")
        except Exception as e:
            failed.append((task_id, 0.0, str(e)))
            print(f"💥 {task_id}: ERROR - {e}")
    
    print(f"\n{'='*70}")
    print(f"MEDIUM TASKS: {len(MEDIUM_TASKS) - len(failed)}/{len(MEDIUM_TASKS)} passed")
    if failed:
        print("Failed tasks:")
        for task_id, reward, reason in failed:
            print(f"  - {task_id}: {reason}")
    print("="*70)
    return len(failed) == 0

def test_all_hard_tasks():
    print("\n" + "="*70)
    print("TESTING ALL HARD TASKS")
    print("="*70)
    failed = []
    for task in HARD_TASKS:
        task_id = task['task_id']
        try:
            # Create a good explanation that matches keywords
            keywords = task.get('explanation_keywords', [])
            explanation = f"The bug involved issues with {', '.join(keywords[:3])}. The fix addresses these problems."
            
            reward, passed, total, feedback, _ = grade_hard(task['fixed_code'], task, explanation)
            if reward < 0.95:  # Allow for some explanation variance
                failed.append((task_id, reward, f"{passed}/{total} tests passed"))
                print(f"❌ {task_id}: reward={reward:.2f} ({passed}/{total})")
            else:
                print(f"✅ {task_id}: reward={reward:.2f} ({passed}/{total})")
        except Exception as e:
            failed.append((task_id, 0.0, str(e)))
            print(f"💥 {task_id}: ERROR - {e}")
    
    print(f"\n{'='*70}")
    print(f"HARD TASKS: {len(HARD_TASKS) - len(failed)}/{len(HARD_TASKS)} passed")
    if failed:
        print("Failed tasks:")
        for task_id, reward, reason in failed:
            print(f"  - {task_id}: {reason}")
    print("="*70)
    return len(failed) == 0

if __name__ == "__main__":
    easy_ok = test_all_easy_tasks()
    medium_ok = test_all_medium_tasks()
    hard_ok = test_all_hard_tasks()
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Easy tasks:   {'✅ PASS' if easy_ok else '❌ FAIL'}")
    print(f"Medium tasks: {'✅ PASS' if medium_ok else '❌ FAIL'}")
    print(f"Hard tasks:   {'✅ PASS' if hard_ok else '❌ FAIL'}")
    print(f"\nOverall:      {'✅ ALL TASKS WORKING' if (easy_ok and medium_ok and hard_ok) else '❌ SOME TASKS FAILING'}")
    print("="*70)
