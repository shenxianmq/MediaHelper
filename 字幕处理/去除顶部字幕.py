import os
import re

folder_path = '/Users/shenxian/Downloads/银魂'
for root, _, files in os.walk(folder_path):
    for file in files:
        if file.endswith('ass'):
            file_path = os.path.join(root,file)
            with open(file_path,'r',encoding='utf-8') as f:
                content = f.read()
            content = re.sub('Dialogue.*?, 50\).*','',content)
            content = content.replace('\n\n\nDialogue','\nDialogue')
            content = content.replace('\n\nDialogue','\nDialogue')
            content = content.replace('\n\nDialogue','\nDialogue')
            content = content.replace('50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0','75,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1')
            with open(file_path,'w',encoding='utf-8') as f:
                f.write(content)
            if 'zh' not in file_path or 'chs' not in file_path:
                new_file_path = file_path.replace('ass','zh.ass').replace('chs.zh','zh')
                os.rename(file_path,new_file_path)
            print(file_path)
