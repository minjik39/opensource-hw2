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
        # 헤더 정규식을 이용해 파일 내 모든 일기를 가장 안전하게 쪼갭니다.
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
            "title": "", # 타이틀은 정렬 후 일괄 자동 부여됨
            "date": iso_date,
            "content": content_delta,
            "isPinned": False
        })
        
    return diaries

def reinit_db_safely():
    # 1. 텍스트 파일 두 개 파싱
    old_diaries = parse_txt('d:\\코딩\\old_diaries.txt', False)
    new_diaries = parse_txt('d:\\코딩\\new_dates.txt', True)
    
    # 2. 합치고 날짜순 정렬
    combined = old_diaries + new_diaries
    combined.sort(key=lambda x: x["date"])
    
    # 3. 유저님이 0장부터 시작하게 파일을 만드셨으므로 순서대로 0장, 1장, 2장... 부여
    payload = {}
    for idx, item in enumerate(combined):
        item["title"] = f"{idx}장"
        payload[item["id"]] = item
        
    url = "https://diray-29ff2-default-rtdb.firebaseio.com/diaries.json"
    
    print(f"총 {len(payload)}개의 데이터베이스를 업로드합니다. 가장 첫 장은 0장, 마지막 장은 {len(payload)-1}장 입니다.")
    
    res = requests.put(url, json=payload)
    res.raise_for_status()
    print(f"✅ 완전 복구 및 최신화 완료! 가장 마지막 장 번호: {len(payload)-1}장")

if __name__ == '__main__':
    reinit_db_safely()
