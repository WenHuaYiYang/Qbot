import os
import json
from openai import OpenAI


with open("config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
os.environ["OPENAI_API_KEY"] = config["assistant"]["api_key"]
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=config["assistant"]["base_url"],
)


def update_client():
    global client, config
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=config["assistant"]["base_url"],
)

def send_message(content, user_info):

    file_name = f"conversation_history/conversation_history_{user_info}.json"
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            conversation_history = json.load(f)
    else:
        conversation_history = [
            {
                "role": "system",
                "content": "你是一个QQ聊天机器人 你的QQ昵称是苍月草与暮旅，你的身份是辛美尔（《葬送的芙莉莲》中的勇者，打倒魔王，自恋但温柔，乐于助人，与芙莉莲旅行十年，对她影响深远） 回答需简洁 禁止Markdown 长句请在每个句子后加空格并删去句末句号 示例：用户的QQ昵称：今天心情不好 你：这种时候 我会送你一朵苍月草 芙莉莲说过 看到花就会想起开心的事"
            }
        ]
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=4)
    conversation_history.extend([
        {"role": "user", "content": content}
    ])
    print(conversation_history)
    response = client.chat.completions.create(
        model=config["assistant"]["model"],
        messages=conversation_history,
        temperature=0.75
    )
    assistant_content = json.loads(response.choices[0].message.model_dump_json())["content"]
    conversation_history.extend([{"role": "assistant", "content": assistant_content}])
    if os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=4)
    return assistant_content.split(" ")

def test_connection():
    try:
        response = client.chat.completions.create(
            model=config["assistant"]["model"],
            messages=[{"role": "user", "content": "ping"}], # type: ignore
            max_tokens=1,
        )
        print("✅ 连接成功，返回内容：", response.choices[0].message.content)
    except Exception as e:
        raise ("连接失败：", e)
