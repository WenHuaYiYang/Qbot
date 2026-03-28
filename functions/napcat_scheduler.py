import json
import os
import subprocess
import logging
import asyncio
import schedule
from datetime import datetime

logger = logging.getLogger(__name__)


def start_napcat():
    """启动 NapCat（Docker 容器方式）"""
    try:
        # 检查容器是否已运行
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", "name=napcat"],
            capture_output=True, text=True
        )
        if result.stdout.strip():
            logging.info("NapCat 容器已经在运行，无需启动")
            return

        # 启动容器
        logging.info("正在启动 NapCat 容器...")
        subprocess.run(["docker", "start", "napcat"], check=True, capture_output=True)
        logging.info("NapCat 启动成功")
    except subprocess.CalledProcessError as e:
        logging.error(f"启动 NapCat 失败: {e.stderr}")
    except Exception as e:
        logging.error(f"启动过程发生异常: {e}")


def stop_napcat():
    """停止 NapCat（Docker 容器方式）"""
    try:
        # 检查容器是否运行
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", "name=napcat"],
            capture_output=True, text=True
        )
        if not result.stdout.strip():
            logging.info("NapCat 容器未运行，无需停止")
            return

        # 停止容器
        logging.info("正在停止 NapCat 容器...")
        subprocess.run(["docker", "stop", "napcat"], check=True, capture_output=True)
        logging.info("NapCat 停止成功")
    except subprocess.CalledProcessError as e:
        logging.error(f"停止 NapCat 失败: {e.stderr}")
    except Exception as e:
        logging.error(f"停止过程发生异常: {e}")

START_TIME = "08:00"
STOP_TIME = "23:00"
if not __name__ == "__main__":
    if not os.path.exists("functions/schedule.json"):
        os.makedirs("functions/schedule.json")
        with open("functions/schedule.json", "w", encoding="utf-8") as f:
            data = {
                    "napcat": {
                        "start_time": "08:00",
                        "stop_time": "23:00"
                    }
                }
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        with open("functions/schedule.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            START_TIME = data.get("napcat").get("start_time")
            STOP_TIME = data.get("napcat").get("stop_time")

# 绑定任务
schedule.every().day.at(START_TIME).do(start_napcat)
schedule.every().day.at(STOP_TIME).do(stop_napcat)


#启动时立即执行一次检查
def initial_check():
    current_hour = datetime.now().hour
    if START_TIME.split(":")[0] <= str(current_hour) < STOP_TIME.split(":")[0]:
        logging.info("当前时间在运行时段内，尝试启动 NapCat...")
        start_napcat()
    else:
        logging.info("当前时间不在运行时段，确保 NapCat 已停止...")
        stop_napcat()


async def run_napcat_schedule():
    logging.info("NapCat 定时调度器已启动")
    initial_check()

    # 主循环
    while True:
        try:
            schedule.run_pending()
            await asyncio.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logging.info("收到中断信号，退出调度器")
            break
        except Exception as e:
            logging.error(f"调度循环异常: {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    with open("schedule.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        START_TIME = data["START_TIME"]
        STOP_TIME = data["STOP_TIME"]
    run_napcat_schedule()
