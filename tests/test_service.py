from app.problems import service


def names(problems):
    return [p.name for p in problems]


def test_default_order_is_newest_contest_first(seeded):
    problems, total = service.list_problems(seeded)
    assert total == 5
    assert names(problems)[0] == "Unrated Puzzle"  # contest 9999
    assert names(problems)[-1] == "Theatre Square"  # contest 1


def test_filter_by_exact_tag(seeded):
    problems, total = service.list_problems(seeded, tag="math")
    assert total == 2
    assert set(names(problems)) == {"Watermelon", "Theatre Square"}


def test_tag_filter_does_not_match_substrings(seeded):
    _, total = service.list_problems(seeded, tag="ma")
    assert total == 0


def test_rating_range_excludes_unrated(seeded):
    problems, total = service.list_problems(seeded, min_rating=800, max_rating=1000)
    assert total == 3
    assert "Unrated Puzzle" not in names(problems)


def test_search_by_name_and_by_code(seeded):
    assert names(service.list_problems(seeded, q="watermelon")[0]) == ["Watermelon"]
    assert names(service.list_problems(seeded, q="466c")[0]) == ["Number of Ways"]


def test_search_treats_percent_literally(seeded):
    assert service.list_problems(seeded, q="%")[1] == 0


def test_pagination(seeded):
    page1, total = service.list_problems(seeded, page=1, page_size=2)
    page3, _ = service.list_problems(seeded, page=3, page_size=2)
    assert total == 5
    assert len(page1) == 2
    assert len(page3) == 1


def test_sort_by_rating_desc(seeded):
    problems, _ = service.list_problems(seeded, sort="rating_desc")
    assert [p.rating for p in problems] == [1700, 1000, 800, 800, None]  # unrated last


def test_tag_counts(seeded):
    counts = dict(service.tag_counts(seeded))
    assert counts["math"] == 2
    assert counts["dp"] == 1
