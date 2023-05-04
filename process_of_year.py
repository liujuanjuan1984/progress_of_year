"""
get the process of year and post to rum group
"""
import calendar
import datetime
import json
import logging
import os
import time

from quorum_data_py import feed
from quorum_mininode_py import MiniNode

__version__ = "0.0.1"

logger = logging.getLogger(__name__)


def days_in_year(year):
    """计算指定年份共有多少天"""
    return 366 if calendar.isleap(year) else 365


def format_datetime(dt):
    """将 datetime 对象转换为指定格式的字符串"""
    return dt.strftime("%Y, %b %d, %H:%M:%S")


def day_of_year(dt):
    """计算指定日期是当年的第几天"""
    return dt.toordinal() - datetime.date(dt.year, 1, 1).toordinal() + 1


def progress_bar(percent, width=30):
    """根据百分比生成进度条"""
    # 计算进度条长度
    bar_length = int(width * percent / 100)
    # 使用全角和半角字符生成进度条
    bar_chars = "█" * bar_length + "▁" * (width - bar_length)
    return f"{bar_chars}{percent:.1f}%"


def get_process(dt=None):
    """获取指定日期的年进度条"""
    today = dt or datetime.datetime.now()
    year = today.year
    days = days_in_year(year)
    process = day_of_year(today)
    percent = round(100 * process / days, 2)
    text = "\n".join(
        [
            f"{year} 进度条 / Year Progress {year}",
            f"{progress_bar(percent)}",
            f"北京时间：{format_datetime(today)}",
        ]
    )
    return text, percent


def read_jsonfile(jsonfile):
    """读取 json 文件"""
    if os.path.exists(jsonfile):
        with open(jsonfile, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    return data


def write_jsonfile(jsonfile, data):
    """写入 json 文件"""
    with open(jsonfile, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class YearProcess:
    """YearProcess"""

    def __init__(self, seed: str, pvtkey: str, jsonfile: str, n: int = 5):
        """n : post every n percent"""
        self.rum = MiniNode(seed, pvtkey)
        self.jsonfile = jsonfile
        self.n = n

    def run(self):
        """run for every day"""
        data = read_jsonfile(self.jsonfile)
        today = str(datetime.date.today())
        if today in data:
            return
        text, percent = get_process()
        if int(percent) % self.n != 0:
            return
        idata = feed.new_post(text)
        resp = self.rum.api.post_content(idata)
        if "trx_id" not in resp:
            return
        for i in range(20):
            trx = self.rum.api.get_trx(resp["trx_id"])
            if trx.get("TrxId") == resp["trx_id"]:
                break
            time.sleep(0.2)
        data[today] = resp["trx_id"]
        write_jsonfile(self.jsonfile, data)
