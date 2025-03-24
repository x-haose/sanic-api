from sanic.errorpages import JSONRenderer

from sanic_api.config.setting import JsonRespSettings


class ErrorJSONRenderer(JSONRenderer):
    json_resp_setting: JsonRespSettings | None = None

    def _generate_output(self, *, full: bool) -> dict:
        data = super()._generate_output(full=full)
        if not self.json_resp_setting or not self.json_resp_setting.use_tml:
            return data

        data = {
            self.json_resp_setting.code_field_name: self.json_resp_setting.error_code,
            self.json_resp_setting.msg_field_name: data["message"],
            self.json_resp_setting.data_field_name: data,
        }
        return data
