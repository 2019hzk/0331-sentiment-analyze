from dataclasses import dataclass
from typing import Literal

RoleId = Literal["insight", "media", "host", "report"]
RESEARCH_AGENT_IDS: tuple[RoleId, ...] = ("insight", "media")

@dataclass(slots=True)
class RoleMetadata:
    """
    职责：定义不同角色Agent信息的
    """
    llm_config_prefix: str  # 模型配置前缀
    display_name: str  # 展示名字


ROLE_METADATA: dict[RoleId, RoleMetadata] = {
    "insight": RoleMetadata(display_name="私域检索专家", llm_config_prefix="INSIGHT_AGENT"),
    "media": RoleMetadata(display_name="公域检索专家", llm_config_prefix="MEDIA_AGENT"),
    "host": RoleMetadata(display_name="主持人研判专家", llm_config_prefix="HOST_AGENT"),
    "report": RoleMetadata(display_name="综合报告引擎", llm_config_prefix="REPORT_ENGINE")
}


def get_role_display_name(role_id: RoleId) -> str:
    """返回角色的中文展示名"""
    return ROLE_METADATA[role_id].display_name
