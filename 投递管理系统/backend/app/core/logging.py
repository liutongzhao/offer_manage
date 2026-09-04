"""日志层：统一结构化输出，禁止散用 print。"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("offer_manage")
