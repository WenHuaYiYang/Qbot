import subprocess
import logging
import schedule
import time
import sys
from datetime import datetime

# 配置日志
LOG_FILE = "/var/log/napcat_scheduler.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)


# ---------- 根据你的 NapCat 部署方式修改以下函数 ----------
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


# ---------- 直接运行二进制方式的函数示例（备用） ----------
def start_napcat_binary():
    """直接运行 NapCat 二进制（需替换实际路径）"""
    try:
        # 检查进程是否已存在
        result = subprocess.run(["pgrep", "-f", "napcat"], capture_output=True)
        if result.returncode == 0:
            logging.info("NapCat 进程已在运行")
            return

        # 启动进程（后台运行）
        logging.info("正在启动 NapCat 进程...")
        subprocess.Popen(
            ["/home/user/napcat/napcat"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # 脱离终端
        )
        logging.info("NapCat 启动成功")
    except Exception as e:
        logging.error(f"启动失败: {e}")


def stop_napcat_binary():
    """终止 NapCat 进程"""
    try:
        # 杀死进程
        subprocess.run(["pkill", "-f", "napcat"], check=True)
        logging.info("NapCat 进程已终止")
    except subprocess.CalledProcessError:
        logging.info("未找到 NapCat 进程，无需停止")
    except Exception as e:
        logging.error(f"停止失败: {e}")


# ---------- 调度配置 ----------
# 设置每天启动和停止的时间（24小时制）
START_TIME = "08:00"  # 早上8点登录
STOP_TIME = "23:00"  # 晚上11点下线

# 绑定任务
schedule.every().day.at(START_TIME).do(start_napcat)
schedule.every().day.at(STOP_TIME).do(stop_napcat)


# 可选：启动时立即执行一次检查（例如确保当前状态与时间匹配）
def initial_check():
    current_hour = datetime.now().hour
    if START_TIME.split(":")[0] <= str(current_hour) < STOP_TIME.split(":")[0]:
        logging.info("当前时间在运行时段内，尝试启动 NapCat...")
        start_napcat()
    else:
        logging.info("当前时间不在运行时段，确保 NapCat 已停止...")
        stop_napcat()


if __name__ == "__main__":
    logging.info("NapCat 定时调度器已启动")
    initial_check()

    # 主循环
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logging.info("收到中断信号，退出调度器")
            break
        except Exception as e:
            logging.error(f"调度循环异常: {e}")
            time.sleep(60)