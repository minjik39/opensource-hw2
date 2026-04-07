import re
import json
import time
import requests
from datetime import datetime, timedelta

def parse_txt(file_path, is_empty_body=False):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp949', errors='ignore') as f:
            content = f.read()
            
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    if is_empty_body:
        blocks = [line for line in content.split('\n') if line.strip()]
    else:
        # Perfectly slice the file everywhere a date header signature appears.
        pattern = r'(?m)^[ \t]*(?:\d+장[ \t]+)?(?:20\d{2}[\.\- 년]+[0-9]{1,2}[\.\- 월]+[0-9]{1,2}일?)'
        matches = list(re.finditer(pattern, content))
        blocks = []
        if matches:
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(content)
                blocks.append(content[start:end].strip())
        else:
            blocks = [content]
            
    fallback_date = datetime(2027, 1, 1, 0, 0)
    diaries = []
    
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block: continue
        
        lines = block.split('\n')
        first_line = lines[0]
        
        y, m, d = None, None, None
        h, mn = "00", "00"
        
        date_match = re.search(r'(20\d{2})[\.\- 년]+(\d{1,2})[\.\- 월]+(\d{1,2})', first_line)
        if date_match:
            y, m, d = date_match.groups()
            
        time_match = re.search(r'(\d{1,2}):(\d{1,2})', first_line)
        if time_match:
            h_raw, mn = time_match.groups()
            hr = int(h_raw)
            if re.search(r'오후|PM|pm', first_line) and hr < 12:
                hr += 12
            elif re.search(r'오전|AM|am', first_line) and hr == 12:
                hr = 0
            h = f"{hr:02d}"
            
        if y and m and d:
            iso_date = f"{y}-{int(m):02d}-{int(d):02d}T{h}:{int(mn):02d}:00.000Z"
        else:
            if is_empty_body:
                continue
            iso_date = fallback_date.strftime("%Y-%m-%dT%H:%M:00.000Z")
            fallback_date += timedelta(days=1)
            
        if is_empty_body:
            body_text = ""
        else:
            body_text = block
            if date_match or re.search(r'\d+장', first_line):
                body_text = '\n'.join(lines[1:])
                header_text_stripped = re.sub(r'(\d+장)|(20\d{2}[\.\- 년]+\d{1,2}[\.\- 월]+\d{1,2}일?)|(\d{1,2}:\d{1,2})|(오전|오후|AM|PM|시간 불명)', '', first_line).strip()
                if header_text_stripped:
                    body_text = header_text_stripped + '\n' + body_text
            body_text = body_text.strip()
            
        content_delta = {"ops": [{"insert": body_text + "\n"}]}
        doc_id = str(int(time.time() * 1000) + id(block) + i)
        
        diaries.append({
            "id": doc_id,
            "title": "",
            "date": iso_date,
            "content": content_delta,
            "isPinned": False
        })
        
    return diaries

def reinit_db():
    old_diaries = parse_txt('d:\\코딩\\old_diaries.txt', False)
    new_diaries = parse_txt('d:\\코딩\\new_dates.txt', True)
    
    combined = old_diaries + new_diaries
    combined.sort(key=lambda x: x["date"])
    
    # "현재 40장의 날짜를 1장으로 시작해서"
    # Find the diary corresponding to 2024.02.14, so it becomes 1장.
    epoch_idx = 0
    for idx, d in enumerate(combined):
        if d["date"].startswith("2024-02-14"):
            epoch_idx = idx
            break
            
    payload = {}
    for idx, item in enumerate(combined):
        # Anchor index gets 1장. An earlier entry gets 0장, etc.
        ch_num = 1 + (idx - epoch_idx)
        item["title"] = f"{ch_num}장"
        payload[item["id"]] = item
        
    url = "https://diray-29ff2-default-rtdb.firebaseio.com/diaries.json"
    
    # We will print the latest number to show the user where it ended.
    max_num = max([1 + (idx - epoch_idx) for idx in range(len(combined))])
    
    print(f"총 {len(payload)}개의 데이터베이스를 업로드합니다. 마지막 장은 {max_num}장 입니다.")
    
    res = requests.put(url, json=payload)
    res.raise_for_status()
    print(f"✅ 완전 복구 및 최신화 완료! 가장 마지막 장 번호: {max_num}장")

if __name__ == '__main__':
    reinit_db()
