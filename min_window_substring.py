"""
LeetCode 76. 最小覆盖子串 (Minimum Window Substring)

给定两个字符串 s 和 t，返回 s 中包含 t 所有字符的最小子串。
如果不存在，返回空字符串 ""。
"""

from collections import Counter


def min_window(s: str, t: str) -> str:
    need = Counter(t)          # t 中每个字符的需求量
    window = {}                # 当前窗口中各字符的计数
    formed = 0                 # 已满足需求的字符种类数
    required = len(need)       # 需要满足的字符种类总数

    left = 0
    min_len = float("inf")
    start = 0

    for right, ch in enumerate(s):
        window[ch] = window.get(ch, 0) + 1

        if ch in need and window[ch] == need[ch]:
            formed += 1

        # 当窗口满足条件时，尝试收缩左边界
        while formed == required:
            cur_len = right - left + 1
            if cur_len < min_len:
                min_len = cur_len
                start = left

            left_ch = s[left]
            window[left_ch] -= 1
            if left_ch in need and window[left_ch] < need[left_ch]:
                formed -= 1
            left += 1

    return "" if min_len == float("inf") else s[start:start + min_len]


if __name__ == "__main__":
    # 测试用例
    print(min_window("ADOBECODEBANC", "ABC"))  # "BANC"
    print(min_window("a", "a"))                 # "a"
    print(min_window("a", "aa"))                # ""
