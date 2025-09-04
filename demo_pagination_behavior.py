#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分页连续失败行为演示
Demonstration of pagination consecutive failures behavior
"""

def demonstrate_old_vs_new_behavior():
    """演示修改前后的行为差异"""
    print("=== 分页连续失败行为对比演示 ===")
    print("Demonstration of Pagination Consecutive Failures Behavior")
    print()
    
    def simulate_pagination(max_consecutive_failures, scenario_name):
        print(f"--- {scenario_name} (max_consecutive_failures = {max_consecutive_failures}) ---")
        
        # 模拟页面获取结果：成功(S)或失败(F)
        # Simulate page fetch results: Success(S) or Failure(F)
        page_results = ['F', 'F', 'S', 'F', 'F', 'F', 'S', 'F', 'F', 'F', 'F']
        
        page = 1
        consecutive_failures = 0
        total_pages_attempted = 0
        successful_pages = 0
        
        print(f"页面获取序列: {' '.join(page_results)}")
        print("Page fetch sequence:", ' '.join(page_results))
        print()
        
        for result in page_results:
            total_pages_attempted += 1
            print(f"第 {page} 页: {result}", end="")
            
            if result == 'S':  # 成功
                consecutive_failures = 0
                successful_pages += 1
                page += 1
                print(f" - 成功，重置连续失败计数")
                print(f"  Page {page-1}: {result} - Success, reset consecutive failures count")
            else:  # 失败
                consecutive_failures += 1
                print(f" - 失败 (连续失败 {consecutive_failures} 次)")
                print(f"  Page {page}: {result} - Failed (consecutive failures: {consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    print(f"*** 连续 {consecutive_failures} 页解析失败，停止翻页 ***")
                    print(f"*** {consecutive_failures} consecutive page failures, stop pagination ***")
                    break
                else:
                    page += 1
        
        print()
        print(f"总计尝试页面: {total_pages_attempted}")
        print(f"成功获取页面: {successful_pages}")
        print(f"Total pages attempted: {total_pages_attempted}")
        print(f"Successfully fetched pages: {successful_pages}")
        print()
        
        return total_pages_attempted, successful_pages
    
    # 演示修改前的行为 (max_consecutive_failures = 2)
    old_attempts, old_successes = simulate_pagination(2, "修改前 (Before)")
    
    print("=" * 60)
    print()
    
    # 演示修改后的行为 (max_consecutive_failures = 3)  
    new_attempts, new_successes = simulate_pagination(3, "修改后 (After)")
    
    print("=" * 60)
    print("=== 总结 Summary ===")
    print(f"修改前 (Before): 尝试了 {old_attempts} 页，成功 {old_successes} 页")
    print(f"修改后 (After):  尝试了 {new_attempts} 页，成功 {new_successes} 页")
    print(f"Before: Attempted {old_attempts} pages, succeeded {old_successes} pages") 
    print(f"After:  Attempted {new_attempts} pages, succeeded {new_successes} pages")
    print()
    
    improvement = new_attempts - old_attempts
    if improvement > 0:
        print(f"✅ 改进：多尝试了 {improvement} 页，提高了数据获取的成功率")
        print(f"✅ Improvement: Attempted {improvement} more pages, increasing data retrieval success rate")
    
    print()
    print("这个修改让爬虫更加持久，在遇到临时网络问题或页面加载问题时")
    print("不会过早放弃，从而能够获取到更多的视频数据。")
    print()
    print("This modification makes the crawler more persistent, not giving up too early")
    print("when encountering temporary network issues or page loading problems,")
    print("allowing it to retrieve more video data.")

if __name__ == "__main__":
    demonstrate_old_vs_new_behavior()