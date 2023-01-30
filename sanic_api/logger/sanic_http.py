from sanic.http import Http
from sanic.log import access_logger


class SanicHttp(Http):
    def log_response(self) -> None:
        """
        自定义输出访问日志
        Returns:

        """
        req, res = self.request, self.response

        dt = (req.ctx.et - req.ctx.st) * 1000
        size = getattr(self, "response_bytes_left", getattr(self, "response_size", -1))
        extra = {
            "status": getattr(res, "status", 0),
            "byte": self.format_size(size),
            "host": "UNKNOWN",
            "request": "nil",
            "time": f"{dt:.4f} ms",
            "req_args": f" args: {req.ctx.api.req_to_json()}" if hasattr(req.ctx, "api") else "",
        }
        if req is not None:
            if req.remote_addr or req.ip:
                extra["host"] = f"{req.remote_addr or req.ip}:{req.port}"
            extra["request"] = f"{req.method} {req.url}"
        access_logger.info("", extra=extra)

    def format_size(self, size: float):
        """
        格式化输出大小
        :param size: 大小
        :return: 返回格式化的字符串
        """
        for count in ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if -1024.0 < size < 1024.0:
                return f"{size:3.1f} {count}"
            size /= 1024.0
        return f"{size:3.1f} YB"
