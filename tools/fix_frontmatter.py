#!/usr/bin/env python
"""
fix_frontmatter.py — 检查并修复所有文章 front matter 中的中文标点

用法:
  python tools/fix_frontmatter.py           # 修复模式：修改文件
  python tools/fix_frontmatter.py --check    # 检查模式：只报告，不改文件，发现问题则退出码 1

功能:
  1. 扫描 content/posts/ 下所有 .md 文件
  2. 在 front matter（+++ 之间）中替换：
     中文逗号 ， → 英文逗号 ,
     中文左引号 " → 英文引号 "
     中文右引号 " → 英文引号 "
  3. 清理 front matter 内多余空行
  4. 输出修复报告
"""

import os
import re
import sys
import argparse
from pathlib import Path


# 中文标点 → 英文标点
REPLACEMENTS = {
    '\u3002': ',',   # ，中文逗号
    '\u201c': '"',   # " 中文左引号
    '\u201d': '"',   # " 中文右引号
    '\uff0c': ',',   # ，全角逗号
    '\u2018': "'",   # ' 中文左单引号
    '\u2019': "'",   # ' 中文右单引号
}


def fix_front_matter(content):
    """修复 front matter 中的中文标点，返回 (修复后内容, 替换次数)"""
    # 匹配 +++ ... +++ 或 --- ... ---
    pattern = re.compile(r'^(\+\+\+)(.*?)(\+\+\+)', re.MULTILINE | re.DOTALL)
    
    total_fixes = 0
    
    def replace_in_frontmatter(match):
        nonlocal total_fixes
        start = match.group(1)
        body = match.group(2)
        end = match.group(3)
        
        fixes = 0
        for cn, en in REPLACEMENTS.items():
            count = body.count(cn)
            if count > 0:
                body = body.replace(cn, en)
                fixes += count
        
        # 清理多余空行（连续空行变成单个空行，首尾空行去掉）
        lines = body.split('\n')
        # 去掉首尾空行
        while lines and lines[0].strip() == '':
            lines.pop(0)
        while lines and lines[-1].strip() == '':
            lines.pop()
        # 连续空行变成单个
        result_lines = []
        prev_empty = False
        for line in lines:
            if line.strip() == '':
                if not prev_empty:
                    result_lines.append(line)
                prev_empty = True
            else:
                result_lines.append(line)
                prev_empty = False
        
        body = '\n'.join(result_lines)
        total_fixes += fixes
        return start + '\n' + body + '\n' + end
    
    fixed = pattern.sub(replace_in_frontmatter, content)
    return fixed, total_fixes


def main():
    parser = argparse.ArgumentParser(description='检查/修复文章 front matter 中的中文标点')
    parser.add_argument('--check', action='store_true', help='检查模式：只报告不修改，发现问题则退出码 1')
    args = parser.parse_args()

    # 确定博客根目录
    script_dir = Path(__file__).parent.resolve()
    blog_dir = script_dir.parent
    posts_dir = blog_dir / 'content' / 'posts'
    
    if not posts_dir.is_dir():
        print(f"错误: 找不到 {posts_dir}")
        sys.exit(1)
    
    md_files = sorted(posts_dir.rglob('*.md'))
    
    if not md_files:
        print("没有找到任何 .md 文件")
        return
    
    fixed_count = 0
    clean_count = 0
    dirty_files = []
    
    for md_file in md_files:
        rel_path = md_file.relative_to(blog_dir)
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content, fixes = fix_front_matter(content)
        
        if fixes > 0:
            if args.check:
                print(f"  [FAIL] {rel_path}  ({fixes} 处中文标点)")
                dirty_files.append(str(rel_path))
            else:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"  修复 {rel_path}  ({fixes} 处中文标点)")
                fixed_count += 1
        else:
            clean_count += 1
    
    mode_label = "检查" if args.check else "修复"
    print(f"\n  扫描 {len(md_files)} 个文件")
    print(f"  {mode_label} {fixed_count if not args.check else len(dirty_files)} 个文件")
    print(f"  无需{mode_label} {clean_count} 个文件")
    
    if args.check:
        if dirty_files:
            print(f"\n  检查未通过！请本地运行: python tools/fix_frontmatter.py")
            sys.exit(1)
        else:
            print(f"\n  全部干净，没有中文标点问题。")
    else:
        if fixed_count > 0:
            print(f"\n  修复完成！现在可以安全 push 了。")
        else:
            print(f"\n  全部干净，没有中文标点问题。")


if __name__ == '__main__':
    main()
