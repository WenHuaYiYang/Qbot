import asyncio
import os
import random
import subprocess
import datetime
import websockets
import json
from functions.chatbot import send_message, test_connection, update_client
from functions.hitokoto import get_hitokoto

with open("config/config.json", "r") as f:
    config = json.load(f)

# 用于暂存待删除文件的映射
pending_files = {}  # echo -> file_path
current_websocket = None

async def send_video_and_delete(websocket, user_id, video_path):
    # 生成唯一标识
    import uuid
    echo = str(uuid.uuid4())
    # 记录文件路径
    pending_files[echo] = video_path

    # 构造 OneBot 消息段
    message = [{
        "type": "video",
        "data": {"file": to_file_url(video_path)}
    }]
    payload = {
        "action": "send_private_msg",
        "params": {"user_id": user_id, "message": message},
        "echo": echo
    }
    await websocket.send(json.dumps(payload))


async def handler(websocket):
    global current_websocket
    current_websocket = websocket
    print("✅ NapCat 已连接！")
    async for response in websocket:
        data = json.loads(response)
        print("收到消息:", data)

        # 如果收到的是事件（如用户消息）
        if data.get("post_type") == "message":
            # 处理消息逻辑...
            await process_message(data, websocket)
            await process_bilibili_card(data, websocket)

        if data.get("post_type") == "request" and data.get("request_type") == "friend":
            await process_friend_add_request(data, websocket)

        if "echo" in data and data["echo"] in pending_files:
            file_path = pending_files.pop(data["echo"])
            if data.get("status") == "ok":
                try:
                    os.remove(file_path[0])
                    print(f"删除成功: {file_path[0]}")
                except Exception as e:
                    print(f"删除失败: {e}")
            else:
                print(f"发送失败，未删除文件: {file_path}")


async def process_friend_add_request(data, websocket):
    user_id = data.get("user_id")
    comment = data.get("comment")
    flag = data.get("flag")

    # 根据验证消息决定是否同意
    if comment == "3月29号":  # 验证消息正确，同意
        response = {
            "action": "set_friend_add_request",
            "params": {
                "flag": flag,
                "approve": True
            }
        }
    else:  # 验证消息不对，拒绝
        response = {
            "action": "set_friend_add_request",
            "params": {
                "flag": flag,
                "approve": False,
                "reason": "请说暗号！"  # 拒绝时可附加理由
            }
        }

    await websocket.send(json.dumps(response))
    print(f"已处理好友请求，用户 {user_id}，验证消息：{comment}")


async def process_message(data, websocket):
    messages = data["message"]
    for message in messages:
        if message["type"] == "text":
            text = data["sender"]["nickname"] + "：" + message["data"]["text"]
            replies = send_message(text, data["sender"]["user_id"])
            print(replies)
            for rep in replies:
                # 发送回复（API 请求格式）
                reply = {
                    "action": "send_private_msg",
                    "params": {
                        "user_id": data.get("user_id"),
                        "message": rep
                    },
                    "echo": "reply_001"
                }
                await websocket.send(json.dumps(reply))
                await asyncio.sleep(random.randrange(2, 4))


def download_bilibili_video(url, output_dir='./downloads'):
    # 使用 --print after_move:filepath 输出最终路径
    cmd = [
        'yt-dlp',
        url,
        '-o', f'{output_dir}/%(title)s.%(ext)s',
        '--merge-output-format', 'mp4',
        '--print', 'after_move:filepath',
        '--quiet'
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        check=False
    )
    if result.returncode == 0:
        # 输出中包含文件路径，可能有多个（如果下载的是播放列表）
        file_paths = result.stdout.strip().split('\n')
        return file_paths
    else:
        raise Exception(f"下载失败: {result.stderr}")


def to_file_url(file_path):
    # 转为绝对路径
    abs_path = os.path.abspath(file_path[0])
    # 将反斜杠替换为正斜杠
    posix_path = abs_path.replace('\\', '/')
    # 构造 file:/// URL
    return f"file:///{posix_path}"


async def process_bilibili_card(data, websocket):
    """
    处理消息中的B站视频卡片（JSON类型），提取信息并回复
    """
    message_segments = data.get("message")
    print("message_segments:"+str(message_segments))
    for seg in message_segments:
        if seg.get("type") == "json":
            json_str = seg.get("data", {}).get("data", "")
            # 提取B站链接
            bili_url = extract_bilibili_url_from_json(json_str)
            reply = {
                "action": "send_private_msg",
                "params": {
                    "user_id": data.get("user_id"),
                    "message": "检测到B站视频，正在下载"
                },
                "echo": "reply_001"
            }

            await websocket.send(json.dumps(reply))

            file_path = download_bilibili_video(bili_url)
            await send_video_and_delete(websocket, data.get("user_id"), file_path)
            print(f"视频发送请求已提交: {file_path}")
            break  # 找到第一个B站卡片后退出


def extract_bilibili_url_from_json(data_str):
    """从json消息段中提取B站视频链接"""
    data = json.loads(data_str)
    meta = data.get("meta")
    detail = meta.get("detail_1")
    qqdocurl = detail.get("qqdocurl", "")
    print("qqdocurl:"+str(qqdocurl))
    return qqdocurl


async def scheduled_signature():
    target_time = "15:30"
    last_run_date = None
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.date()
        if current_time == target_time and last_run_date != today and current_websocket:
            data = get_hitokoto()
            hitokoto = data.get("hitokoto", None)
            from_where = data.get("from_where", "无题")
            from_who= data.get("from_who", "无名氏")
            if hitokoto and from_where and from_who:
                payload = {
                    "action": "set_diy_online_status",
                    "params": {"status": f"{hitokoto} ——《{from_where}》（{from_who}）"},
                    "echo": "signature_auto"
                }
                await current_websocket.send(json.dumps(payload))
                print(f"[{now}] 已发送签名修改请求")
                last_run_date = today
        await asyncio.sleep(60)


async def main():
    asyncio.create_task(scheduled_signature())
    async with websockets.serve(handler, config["websockets"]["host"], config["websockets"]["port"]):
        print("WebSocket 服务器已启动，等待 NapCat 连接...")
        await asyncio.Future()  # 永久运行


if __name__ == "__main__":
    if not config.get("initialized"):
        print("----模型初始化----")
        base_url = input("请输入base_url:")
        api_key = input("请输入api_key:")
        model = input("请输入model:")
        config["assistant"] = {
            "base_url": base_url,
            "api_key": api_key,
            "model": model
        }
        with open("config/config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        update_client()
        test_connection()
        print("---websockets初始化---")
        host = input("请输入host:")
        port = input("请输入port:")
        config["websockets"] = {
            "host": host,
            "port": port
        }
        config["initialized"] = True
        with open("config/config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        asyncio.run(main())
    else:
        asyncio.run(main())

