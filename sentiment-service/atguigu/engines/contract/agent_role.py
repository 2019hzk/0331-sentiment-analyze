from dataclasses import dataclass
from typing import Literal

AgentInfoRoleKey = Literal["insight", "media", "host", "report"]


@dataclass(slots=True)
class AgentRoleInfo:
    """
    职责：定义不同角色Agent信息的
    """
    config_prefix: str  # 配置信息
    display_name: str  # 展示名字


AGENT_ROLE_INFOS: dict[AgentInfoRoleKey, AgentRoleInfo] = {
    "insight": AgentRoleInfo(display_name="私域检索专家", config_prefix="INSIGHT_AGENT"),
    "media": AgentRoleInfo(display_name="公域检索专家", config_prefix="MEDIA_AGENT"),
    "host": AgentRoleInfo(display_name="主持人研判专家", config_prefix="HOST_AGENT"),
    "report": AgentRoleInfo(display_name="综合报告引擎", config_prefix="REPORT_ENGINE")
}
