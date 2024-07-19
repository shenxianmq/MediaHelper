import os
import sys
import re

if __name__ == '__main__':
    ass_path = sys.argv[1]
    double_language = True
    with open(ass_path,'r',encoding='utf-8') as f:
        sub_text = f.read()
    font_name = 'STKaiti'
    font_size = '20'
    out_line = '2'
    margin_v = '15'
    chi_eng_style = f"Style: Default,{font_name},{font_size},&H00FFFFFF,&HF0000000,&H006C3300,&H00000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,15,134\nStyle: Eng,Cronos Pro Subhead,14,&H3CF1F3,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,{out_line},2,0,0,{margin_v},1"
    chi_style = f"Style: Default,{font_name},{font_size},&H00FFFFFF,&HF0000000,&H006C3300,&H00000000,0,0,0,0,100,100,0,0,1,2,1,2,5,5,{margin_v},134"
    sub_text = re.sub("Style:.*?\n","",sub_text)
    sub_text = re.sub("{[^}]+}", "",sub_text)
    if double_language:
        defautl_style = chi_eng_style
        sub_text = sub_text.replace("\\N", "\\N{\\rEng}")
    else:
        defautl_style = chi_style
    sub_text = re.sub("Encoding",f"Encoding\n{defautl_style}",sub_text)
    with open(ass_path,'w',encoding='utf-8') as f:
        f.write(sub_text)
    print("字幕修改成功")