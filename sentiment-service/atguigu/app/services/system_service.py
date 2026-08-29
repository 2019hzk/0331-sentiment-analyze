import os
from typing import Any

from atguigu.engines.contract.settings import get_settings, ENV_FILE, reload_setting
from dotenv import set_key

ALLOWED_CONFIG_KEYS = [
    "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
    "INSIGHT_ENGINE_API_KEY", "INSIGHT_ENGINE_BASE_URL", "INSIGHT_ENGINE_MODEL_NAME", "INSIGHT_ENGINE_MODEL_PROVIDER",
    "MEDIA_ENGINE_API_KEY", "MEDIA_ENGINE_BASE_URL", "MEDIA_ENGINE_MODEL_NAME", "MEDIA_ENGINE_MODEL_PROVIDER",
    "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
    "HOST_API_KEY", "HOST_BASE_URL", "HOST_MODEL_NAME", "HOST_MODEL_PROVIDER",
    "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
]


def mark_secret(value: str) -> str:
    """
    职责:API_KEY值得处理
    :param value:
    :return:
    """
    if not value:
        return ""

    return f"****{value[-4:]}"


class SystemService:

    def get_config(self) -> dict[str, Any]:
        """
        读取配置信息
        :return:
        """
        settings = get_settings()

        config_dict: dict[str, Any] = {}

        for key in ALLOWED_CONFIG_KEYS:
            value = getattr(settings, key, None)

            text = "" if value is None else value

            if key.endswith("_API_KEY"):
                text = mark_secret(value)

            config_dict[key] = text

        return config_dict

    def update_config(self, config_info: dict[str, Any]):
        """
        更新配置信息
        :param config_info:
        :return:
        """
        # 1. 防御性校验
        unknown_keys = [key for key in config_info.keys() if key not in ALLOWED_CONFIG_KEYS]

        if unknown_keys:
            raise ValueError(f"位置的配置属性{'、'.join(unknown_keys)}")

        # 2. 更新配置信息
        for key, value in config_info.items():
            set_key(ENV_FILE, key, value,quote_mode="never")  # env文件
            os.environ[key] = value  # 环境变量

        # 3. 重新更新配置类
        reload_setting()


if __name__ == '__main__':
    list_data = "abcde"
    print(list_data[-2:])
