import os
import time
import requests
import json


HISTORY_FILE="hitokoto_history.json"

def load_history() -> list:
    """加载历史记录文件"""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("history", [])


def save_history(history_ids, last_date):
    """保存历史记录"""
    global HISTORY_FILE
    data = {
        "history": history_ids,
        "last_date": last_date
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_hitokoto():
    global HISTORY_FILE
    url = "https://v1.hitokoto.cn/?c=i"
    history_ids = load_history()
    for attempt in range(20):
        result = requests.get(url).json()
        if not result:
            continue
        # 检查 id 是否重复
        if result["uuid"] not in history_ids:
            history_ids.append(result["uuid"])
            save_history(history_ids, str(time.time()))
            return result
        print(f"第 {attempt + 1} 次尝试：句子重复，重新获取...")
    return None

if __name__ == "__main__":
    for i in range(20):
        print(get_hitokoto())