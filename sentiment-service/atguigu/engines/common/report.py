from pathlib import Path
from atguigu.engines.contract.agent_role import AgentInfoRoleKey
from atguigu.engines.contract.settings import get_settings


def get_report_dir(task_id: str, role: AgentInfoRoleKey) -> str:
    return str(Path(get_settings().RUNTIME_DIR) / f"{task_id}" / f"{role}")
