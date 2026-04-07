import re

def check_old_diaries():
    file_path = 'd:\\코딩\\old_diaries.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp949', errors='ignore') as f:
            content = f.read()
            
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    matches = re.finditer(r'(?:\b(\d+)장\s+)?20\d{2}[ \.\-년]+\d{1,2}[ \.\-월]+\d{1,2}일?', content)
    
    nums = []
    missing_nums = 0
    for m in matches:
        if m.group(1):
            nums.append(int(m.group(1)))
        else:
            missing_nums += 1
            
    print(f"Total explicitly numbered N장: {len(nums)}")
    print(f"Total dates without N장: {missing_nums}")
    print(f"Numbers found: {nums}")
    print(f"Min number: {min(nums) if nums else 'None'}")
    print(f"Max number: {max(nums) if nums else 'None'}")

if __name__ == '__main__':
    check_old_diaries()
