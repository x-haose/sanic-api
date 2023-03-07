from sanic import Request
from sanic.http import Http
from sanic.log import access_logger

from sanic_api.utils import json_dumps


class SanicHttp(Http):
    def log_response(self) -> None:
        """
        自定义输出访问日志
        Returns:

        """
        req, res = self.request, self.response

        dt = (req.ctx.et - req.ctx.st) * 1000
        size = getattr(self, "response_bytes_left", getattr(self, "response_size", -1))
        req_args = self.get_req_args(req)
        extra = {
            "status": getattr(res, "status", 0),
            "byte": self.format_size(size),
            "host": "UNKNOWN",
            "request": "nil",
            "time": f"{dt:.4f} ms",
            "req_args": f" args: {req_args}" if req_args else "",
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

    def get_req_args(self, request: Request) -> str:
        """
        获取请求参数
        Args:
            request: 请求

        Returns:
            返回具有 json、query、form参数的json
        """
        data = {}
        for attr in ["args", "form"]:
            attr_data = {}
            for k, v in getattr(request, attr).items():
                if type(v) == list and len(v) == 1:
                    attr_data[k] = v[0]
                else:
                    attr_data[k] = v
            if attr_data:
                data[attr] = attr_data
        if request.json:
            data["json"] = request.json

        return json_dumps(data) if data else ""
