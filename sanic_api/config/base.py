import json
from abc import ABC
from configparser import ConfigParser
from pathlib import Path
from typing import Any, ClassVar, Dict, Tuple, Type

import yaml
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from sanic_api.utils import getpath_by_root


class CustomSettingsSource(PydanticBaseSettingsSource, ABC):
    """
    自定义的配置文件来源基类
    """

    def __init__(
        self,
        settings_cls: Type[BaseSettings],
        path: Path,
    ):
        super().__init__(settings_cls)
        self.path = path
        self.encoding = self.config.get("env_file_encoding")
        self.src_dict = self.get_src_dict()

    def get_src_dict(self) -> Dict[str, Any]:
        return {}

    def get_field_value(self, field: FieldInfo, field_name: str) -> Tuple[Any, str, bool]:
        field_value = self.src_dict.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        return value

    def __call__(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(field, field_name)
            field_value = self.prepare_field_value(field_name, field, field_value, value_is_complex)
            if field_value is not None:
                data[field_key] = field_value

        return data


class JsonSettingsSource(CustomSettingsSource):
    """
    Json文件来源导入配置项
    """

    def get_src_dict(self) -> Dict[str, Any]:
        return json.loads(self.path.read_text(self.encoding))


class IniSettingsSource(CustomSettingsSource):
    """
    ini文件来源导入配置项
    """

    def get_src_dict(self) -> Dict[str, Any]:
        parser = ConfigParser()
        parser.read(self.path, self.encoding)
        return getattr(parser, "_sections", {}).get("settings", {})


class YamlSettingsSource(CustomSettingsSource):
    """
    Yaml文件来源导入配置项
    """

    def get_src_dict(self) -> Dict[str, Any]:
        return yaml.safe_load(self.path.read_text(self.encoding))


class SettingsBase(BaseSettings):
    """
    项目设置的基类
    """

    _root_config_dir: ClassVar[Path] = getpath_by_root("./configs")
    model_config = SettingsConfigDict(
        env_file=str(_root_config_dir / ".env"), env_file_encoding="utf-8", env_nested_delimiter="__"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # 默认的设置
        default_settings = {
            env_settings,
            init_settings,
            file_secret_settings,
        }

        # json 配置文件
        json_file = cls._root_config_dir / "settings.json"
        if json_file.exists():
            json_settings_source = JsonSettingsSource(settings_cls, json_file)
            default_settings.add(json_settings_source)

        # ini配置文件
        ini_file = cls._root_config_dir / "settings.ini"
        if ini_file.exists():
            ini_settings_source = IniSettingsSource(settings_cls, ini_file)
            default_settings.add(ini_settings_source)

        # yaml配置文件
        yaml_file = cls._root_config_dir / "settings.yaml"
        if yaml_file.exists():
            yaml_settings_source = YamlSettingsSource(settings_cls, yaml_file)
            default_settings.add(yaml_settings_source)

        return tuple(default_settings)
