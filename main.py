import asyncio
import random
import websockets
import json
from chatbot import send_message, test_connection, update_client

with open("config/config.json", "r") as f:
    config = json.load(f)


async def handler(websocket):
    print("✅ NapCat 已连接")
    async for response in websocket:
        data = json.loads(response)
        print("收到消息:", data)

        # 如果收到的是事件（如用户消息）
        if data.get("post_type") == "message":
            # 处理消息逻辑...
            await process_message(data, websocket)

        if data.get("post_type") == "request" and data.get("request_type") == "friend":
            await process_friend_add_request(data, websocket)


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


async def main():
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

