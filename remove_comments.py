#  Developed by t.me/napaaextra
#  Developed by t.me/napaaextra
import os
import glob

def remove_comments(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if '#' in line:
            line = line.split('#')[0].rstrip() + '\n'
        new_lines.append(line)
    with open(file_path, 'w') as f:
        f.writelines(new_lines)

py_files = glob.glob('**/*.py', recursive=True)
for file in py_files:
    remove_comments(file)
    print(f"Processed {file}")