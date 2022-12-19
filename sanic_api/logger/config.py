import logging
import logging.config

from loguru import logger
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.sql import PostgresLexer


class InterceptHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        fmt = "(%(name)s) %(message)s"
        sanic_access_fmt = (
            "(%(name)s) [%(host)s]: %(request)s %(message)s %(status)d %(byte)s %(time)s args: %(req_args)s"
        )
        fmt = fmt if record.name != "sanic.access" else sanic_access_fmt
        formatter = logging.Formatter(fmt=fmt)
        msg = formatter.format(record)
        msg = self.highlight_sql(record, msg)

        if "Dispatching signal" not in msg:
            logger.opt(depth=depth, exception=record.exc_info).log(level, msg)

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
