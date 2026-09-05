import pytest
from pydantic import ValidationError

from atguigu.engines.media_agent.search_plan import MediaSearchPlanItem


def _plan_item(search_keywords: list[str]) -> MediaSearchPlanItem:
    return MediaSearchPlanItem(
        search_tool="source_search",
        search_keywords=search_keywords,
    )


def test_search_keywords_are_normalized() -> None:
    item = _plan_item(["  2024   时间安排  ", "各省考试政策变化"])

    assert item.search_keywords == ["2024 时间安排", "各省考试政策变化"]


@pytest.mark.parametrize(
    "search_keywords",
    [
        ["   "],
        ["教育部公告", "教育部公告"],
        ["政策 OR 热度"],
        ["时间安排，教育部公告"],
        ["超" * 51],
    ],
)
def test_search_keywords_reject_invalid_phrases(
        search_keywords: list[str],
) -> None:
    with pytest.raises(ValidationError):
        _plan_item(search_keywords)


def test_search_keywords_must_be_a_list() -> None:
    with pytest.raises(ValidationError):
        MediaSearchPlanItem(
            search_tool="source_search",
            search_keywords="2024 时间安排",  # type: ignore[arg-type]
        )
