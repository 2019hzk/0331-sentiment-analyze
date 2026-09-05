from atguigu.engines.media_agent.nodes.section_search_node import (
    _build_search_queries,
)


def test_build_search_queries_removes_repeated_topic_and_duplicates() -> None:
    queries = _build_search_queries(
        "高考",
        [
            "高考 2024 时间安排",
            "各省考试政策变化",
            "高考 2024 时间安排",
            "高考",
        ],
    )

    assert queries == [
        "高考 2024 时间安排",
        "高考 各省考试政策变化",
        "高考",
    ]


def test_build_search_queries_normalizes_whitespace() -> None:
    queries = _build_search_queries(
        "  高考  改革 ",
        ["  教育部   公告  "],
    )

    assert queries == ["高考 改革 教育部 公告"]
