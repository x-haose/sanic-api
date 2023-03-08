import logging
import logging.config
import sys
from types import FrameType
from typing import Optional, Union

import sanic.exceptions
from loguru import logger
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.sql import PostgresLexer
from sanic import Request


class InterceptHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level: Union[int, str] = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        # noinspection PyProtectedMember,PyUnresolvedReferences
        frame: Optional[FrameType] = sys._getframe(6)
        depth: int = 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        fmt = "%(message)s"
        sanic_access_fmt = "[%(host)s]: %(request)s %(message)s %(status)d %(byte)s %(time)s%(req_args)s"
        fmt = fmt if record.name != "sanic.access" else sanic_access_fmt
        formatter = logging.Formatter(fmt=fmt)
        msg = formatter.format(record)
        msg = self.highlight_sql(record, msg)
        req_id = self.get_req_id()

        if "Dispatching signal" not in msg:
            etxra_data = {"type": record.name, "req_id": req_id}
            logger.bind(**etxra_data).opt(depth=depth, exception=record.exc_info).log(level, msg)

    @staticmethod
    def get_req_id():
        """
        获取请求ID
        """
        try:
            req = Request.get_current()
            req_id = f" [{req.id}] "
        except sanic.exceptions.ServerError:
            req_id = " "
        return req_id

    def highlight_sql(self, record: logging.LogRecord, message: str):
        """
        打印日志时高亮SQl
        Args:
            record: 日志记录
            message: 日志消息

        Returns:

        """
        name = record.name
        postgres = PostgresLexer()
        terminal_formatter = TerminalFormatter()

        if name == "tortoise.db_client":
            if (
                record.levelname == "DEBUG"
                and not message.startswith("Created connection pool")
                and not message.startswith("Closed connection pool")
            ):
                message = highlight(message, postgres, terminal_formatter).rstrip()

        return message
