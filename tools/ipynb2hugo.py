#!/usr/bin/env python
"""
ipynb2hugo.py — 将 Jupyter Notebook 一键转换为 Hugo 博客文章

用法:
  python tools/ipynb2hugo.py <ipynb文件路径> [--tags 标签1,标签2] [--category 分类]

示例:
  python tools/ipynb2hugo.py "E:/code/Projects/MachineLearning/ch02_base/feature/1_低方差.ipynb" --tags 机器学习,特征工程 --category 机器学习

流程:
  1. jupyter nbconvert 将 .ipynb 转为 .md
  2. 自动添加 Hugo front matter（标题、日期、标签、math=true）
  3. 创建 Page Bundle 目录 (content/posts/<标题>/index.md)
  4. 复制图片文件夹（如有 matplotlib 输出）
"""

import os
import sys
import re
import shutil
import subprocess
import argparse
import tempfile
from datetime import datetime
from pathlib import Path


def extract_title(filename):
    """从文件名提取标题：去掉数字前缀和扩展名"""
    name = Path(filename).stem
    # 去掉开头的数字和下划线/横线，如 "1_低方差" -> "低方差", "03-data-clean" -> "data-clean"
    name = re.sub(r'^\d+[_\-\s]*', '', name)
    return name


def find_python():
    """找到带有 nbconvert 的 Python 解释器"""
    # 优先用 miniconda3 的 python（nbconvert 装在那里）
    candidates = [
        r'C:\Users\53609\miniconda3\python.exe',
        sys.executable,
        'python',
    ]
    for py in candidates:
        try:
            result = subprocess.run(
                [py, '-c', 'import nbconvert; print(nbconvert.__version__)'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return py
        except Exception:
            continue
    print("错误: 找不到安装了 nbconvert 的 Python 环境")
    print("请确保已安装 jupyter/nbconvert: pip install nbconvert")
    sys.exit(1)


def run_nbconvert(python_exe, ipynb_path, output_dir):
    """用 nbconvert 将 ipynb 转为 markdown"""
    cmd = [
        python_exe, '-m', 'jupyter', 'nbconvert',
        '--to', 'markdown',
        '--output-dir', output_dir,
        ipynb_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"nbconvert 转换失败:\n{result.stderr}")
        sys.exit(1)


def create_front_matter(title, tags, category):
    """生成 TOML 格式的 Hugo front matter"""
    date = datetime.now().strftime('%Y-%m-%d')

    lines = ['+++']
    lines.append(f'title = "{title}"')
    lines.append(f'date = {date}')
    lines.append('draft = false')

    if tags:
        tags_str = ', '.join([f'"{t}"' for t in tags])
        lines.append(f'tags = [{tags_str}]')

    if category:
        lines.append(f'categories = ["{category}"]')

    lines.append('math = true')
    lines.append('+++')
    lines.append('')

    return '\n'.join(lines)


def fold_long_outputs(content, threshold=15):
    """将超过 threshold 行的代码输出折叠为 <details> 标签

    nbconvert 生成的 markdown 中，代码块后的输出以 4 空格缩进呈现。
    本函数检测这些输出块，超过阈值行数的用 <details><summary> 折叠。
    """
    lines = content.split('\n')
    result = []
    i = 0
    in_code_block = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测代码块围栏
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                result.append(line)
                i += 1
                continue
            else:
                # 代码块结束，检查后面是否有输出
                in_code_block = False
                result.append(line)
                i += 1

                # 跳过空行，找到输出区域
                j = i
                while j < len(lines) and lines[j].strip() == '':
                    j += 1

                # 收集输出行（4 空格缩进）
                output_lines = []
                while j < len(lines) and lines[j].startswith('    '):
                    output_lines.append(lines[j][4:])
                    j += 1

                # 去掉末尾空行
                while output_lines and output_lines[-1].strip() == '':
                    output_lines.pop()

                if not output_lines:
                    continue

                if len(output_lines) > threshold:
                    # 折叠长输出
                    result.append('')
                    result.append(
                        f'<details><summary>📎 输出（{len(output_lines)} 行，点击展开）</summary>'
                    )
                    result.append('')
                    result.append('<pre>')
                    result.extend(output_lines)
                    result.append('</pre>')
                    result.append('')
                    result.append('</details>')
                    result.append('')
                    i = j
                else:
                    # 短输出保持原样
                    result.append('')
                    for ol in output_lines:
                        result.append('    ' + ol)
                    result.append('')
                    i = j
                continue

        result.append(line)
        i += 1

    return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(
        description='将 .ipynb 一键转换为 Hugo 博客文章（Page Bundle 结构）'
    )
    parser.add_argument('ipynb', help='.ipynb 文件路径')
    parser.add_argument('--tags', default='', help='标签，逗号分隔（如：机器学习,特征工程）')
    parser.add_argument('--category', default='', help='分类（如：机器学习）')
    parser.add_argument('--fold', type=int, default=15, help='输出超过多少行则折叠（默认 15，设 0 为不折叠）')
    parser.add_argument('--blog-dir', default=None, help='博客项目根目录（默认自动检测）')
    args = parser.parse_args()

    ipynb_path = os.path.abspath(args.ipynb)
    if not os.path.exists(ipynb_path):
        print(f"错误: 文件不存在: {ipynb_path}")
        sys.exit(1)

    # 确定博客根目录
    if args.blog_dir:
        blog_dir = args.blog_dir
    else:
        # 脚本在 tools/ 下，博客根目录是上级
        script_dir = os.path.dirname(os.path.abspath(__file__))
        blog_dir = os.path.dirname(script_dir)

    content_posts_dir = os.path.join(blog_dir, 'content', 'posts')
    if not os.path.isdir(content_posts_dir):
        print(f"错误: 找不到 content/posts/ 目录: {content_posts_dir}")
        print("请确认博客根目录是否正确")
        sys.exit(1)

    # 提取标题
    title = extract_title(ipynb_path)
    print(f"  标题: {title}")

    # 解析标签
    tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else []
    category = args.category.strip() if args.category else ''

    # 找到有 nbconvert 的 Python
    python_exe = find_python()

    # 临时目录用于 nbconvert 输出
    temp_dir = tempfile.mkdtemp(prefix='ipynb2hugo_')

    try:
        # 运行 nbconvert
        print(f"  转换中: {Path(ipynb_path).name}")
        run_nbconvert(python_exe, ipynb_path, temp_dir)

        # 找到生成的 .md 文件
        md_name = Path(ipynb_path).stem + '.md'
        md_path = os.path.join(temp_dir, md_name)

        if not os.path.exists(md_path):
            print(f"错误: 未找到转换后的 .md 文件")
            print(f"  临时目录内容: {os.listdir(temp_dir)}")
            sys.exit(1)

        # 读取转换后的内容
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 折叠长输出
        if args.fold > 0:
            content = fold_long_outputs(content, threshold=args.fold)
            print(f"  长输出折叠阈值: {args.fold} 行")

        # 创建 Page Bundle 目录
        post_dir = os.path.join(content_posts_dir, title)
        os.makedirs(post_dir, exist_ok=True)

        # 添加 front matter
        front_matter = create_front_matter(title, tags, category)
        final_content = front_matter + content

        # 复制图片文件夹（如果有）→ 统一命名为 images/
        files_dir_name = Path(ipynb_path).stem + '_files'
        files_dir_path = os.path.join(temp_dir, files_dir_name)
        if os.path.exists(files_dir_path):
            dest_files_dir = os.path.join(post_dir, 'images')
            if os.path.exists(dest_files_dir):
                shutil.rmtree(dest_files_dir)
            shutil.copytree(files_dir_path, dest_files_dir)
            img_count = sum(1 for f in os.listdir(dest_files_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.svg')))
            print(f"  已复制图片: images/ ({img_count} 张)")
            # 更新 md 中的图片引用路径：<旧目录名>/ → images/
            final_content = re.sub(r'!\[([^\]]*)\]\([^)]*_files/', r'!\1](images/', final_content)
        else:
            print(f"  无图片输出")

        # 写入 index.md
        index_path = os.path.join(post_dir, 'index.md')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"  已创建: content/posts/{title}/index.md")

        print(f"\n  完成!")
        print(f"  文章路径: content/posts/{title}/")
        print(f"  本地预览: cd {blog_dir} && hugo server")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
