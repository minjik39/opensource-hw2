import re
import json
import time
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
        # Split on headers
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
            
        parsed_title = ""
        title_match = re.search(r'(\d+)장', first_line)
        if title_match:
            parsed_title = f"{title_match.group(1)}장"
            
        if is_empty_body:
            body_text = ""
        else:
            body_text = block
            if date_match or title_match:
                body_text = '\n'.join(lines[1:])
                header_text_stripped = re.sub(r'(\d+장)|(20\d{2}[\.\- 년]+\d{1,2}[\.\- 월]+\d{1,2}일?)|(\d{1,2}:\d{1,2})|(오전|오후|AM|PM|시간 불명)', '', first_line).strip()
                if header_text_stripped:
                    body_text = header_text_stripped + '\n' + body_text
            body_text = body_text.strip()
            
        content_delta = {"ops": [{"insert": body_text + "\n"}]}
        doc_id = str(int(time.time() * 1000) + id(block) + i)
        
        diaries.append({
            "id": doc_id,
            "title": parsed_title,
            "date": iso_date,
            "content": content_delta,
            "isPinned": False,
            "is_new": is_empty_body
        })
        
    return diaries

def simulate_migration():
    old_diaries = parse_txt('d:\\코딩\\old_diaries.txt', False)
    new_diaries = parse_txt('d:\\코딩\\new_dates.txt', True)
    
    combined = old_diaries + new_diaries
    combined.sort(key=lambda x: x["date"])
    
    # We will strictly map indices such that index 0 is "0장", index 1 is "1장"
    # because the user literally changed the text file to start from 0장!
    payload = {}
    for idx, item in enumerate(combined):
        item["calculated_title"] = f"{idx}장"
        if "is_new" in item:
            del item["is_new"]
        payload[item["id"]] = item
        
    with open('d:\\코딩\\final_simulation.json', 'w', encoding='utf-8') as f:
        json.dump(list(payload.values()), f, ensure_ascii=False, indent=2)
        
    print(f"Total diaries calculated: {len(payload)}")

if __name__ == '__main__':
    simulate_migration()
