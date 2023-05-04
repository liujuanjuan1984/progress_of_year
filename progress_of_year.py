"""
get the progress of year and post to rum group
"""
import calendar
import datetime
import json
import logging
import os
import time

from quorum_data_py import feed
from quorum_mininode_py import MiniNode

__version__ = "0.1.1"

logger = logging.getLogger(__name__)


def progress_bar(percent, width=30):
    """根据百分比生成进度条"""
    # 计算进度条长度
    bar_length = int(width * percent / 100)
    # 使用全角和半角字符生成进度条
    bar_chars = "█" * bar_length + "▁" * (width - bar_length)
    return f"{bar_chars}{percent:.1f}%"


class YearProgress:
    """YearProgress"""

    def __init__(self, seed: str, pvtkey: str, jsonfile: str, n: int = 5):
        """n : post every n percent"""
        self.rum = MiniNode(seed, pvtkey)
        self.jsonfile = jsonfile
        self.n = n

    def run(self):
        """run for every day"""
        if os.path.exists(self.jsonfile):
            with open(self.jsonfile, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        today = datetime.datetime.now()
        year = today.year
        days = 366 if calendar.isleap(year) else 365
        progress = today.toordinal() - datetime.date(today.year, 1, 1).toordinal() + 1
        percent = round(100 * progress / days, 2)
        text = "\n".join(
            [
                f"{year} 进度条 / Year Progress {year}",
                f"{progress_bar(percent)}",
                f"北京时间：{today.strftime('%Y, %b %d, %H:%M:%S')}",
            ]
        )

        percent = int(percent)
        year = str(year)
        today = str(datetime.date.today())
        if year not in data:
            data[year] = {"sent_days": {}, "sent_progress": []}
        if today in data[year]["sent_days"]:
            return
        if percent in data[year]["sent_progress"]:
            return
        if percent % self.n != 0:
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
        data[year]["sent_days"][today] = resp["trx_id"]
        data[year]["sent_progress"].append(percent)

        with open(self.jsonfile, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
