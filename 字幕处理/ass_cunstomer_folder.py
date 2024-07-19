import os
import re
import pyperclip

if __name__ == '__main__':
    folder_path = pyperclip.paste()
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.ass'):
                ass_path = os.path.join(root, file)
                with open(ass_path,'r',encoding='utf-8') as f:
                    sub_text = f.read()
                # defautl_style = "Style: Default,Arial,22,&H00FFFFFF,&HF0000000,&H006C3300,&H00000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,5,134\nStyle: Eng,Arial,13,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,1,2,0,0,3,1"
                defautl_style = "Style: Default,STKaiti,20,&H00FFFFFF,&HF0000000,&H006C3300,&H00000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,15,134\nStyle: Eng,Microsoft YaHei,14,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0.3,0.1,2,0,0,3,1"
                sub_text = re.sub("{[^}]+}", "",sub_text)
                sub_text = re.sub("Style: Default,.*",defautl_style,sub_text)
                sub_text = sub_text.replace("\\N", "\\N{\\rEng}")
                with open(ass_path,'w',encoding='utf-8') as f:
                    f.write(sub_text)
                print(f"{ass_path}字幕修改成功")