import re

def format_srt_time(time_str):
    hours, minutes, seconds, milliseconds = re.match(r'(\d+:)?(\d{1,2}:)?(\d{1,2}),(\d+)', time_str).groups()
    if not hours:
        hours = '00:'
    if not minutes:
        minutes = '00:'
    return f"{hours.zfill(3)}{minutes.zfill(3)}{seconds.zfill(2)},{milliseconds}"


with open('/Users/shenxian/Downloads/新建文件夹 (2)/index.html','r',encoding='utf-8') as f:
    content= f.read()
res = re.findall('#\d+:(\d+:?.*\d+)<d',content)
result = []
j = 0
for i in res:
    j += 1
    start,end = i.split('->')
    start = format_srt_time(start)
    end = format_srt_time(end)
    time_line = f'{j}\n{start} --> {end}\n\n'
    result.append(time_line)
with open('/Users/shenxian/Desktop/sub.srt','w',encoding='utf-8') as f:
    f.write(''.join(result))
