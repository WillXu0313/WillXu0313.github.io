import os
from datetime import datetime

def has_front_matter(lines):
    return lines and lines[0].strip() == "---"

def generate_front_matter(title, file_mtime):
    formatted_time = datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return [
        "---\n",
        f"title: {title}\n",
        f"date: {formatted_time}\n",
        "categories:\n",
        "- \n",
        "---\n"
    ]

def process_md_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if has_front_matter(lines):
        print(f"跳过已有 Front Matter 的文件: {filepath}")
        return

    filename = os.path.splitext(os.path.basename(filepath))[0]
    mtime = os.path.getmtime(filepath)  # 获取最后修改时间（秒级时间戳）
    front_matter = generate_front_matter(filename, mtime)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(front_matter + ["\n"] + lines)

    print(f"已处理: {filepath}")

def process_directory_recursive(directory):
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                process_md_file(filepath)

# 修改为你的目录路径
your_md_directory = "D:\SelfStudyPackage\hexo-blog\source\_posts"
process_directory_recursive(your_md_directory)
