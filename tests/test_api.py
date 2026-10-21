def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_problems(client, seeded):
    body = client.get("/api/problems", params={"tag": "math", "sort": "rating_asc"}).json()
    assert body["total"] == 2
    assert [p["name"] for p in body["items"]] == ["Watermelon", "Theatre Square"]
    first = body["items"][0]
    assert first["url"] == "https://codeforces.com/problemset/problem/4/A"
    assert first["tags"] == ["math", "brute force"]


def test_list_problems_validates_page_size(client):
    assert client.get("/api/problems", params={"page_size": 1000}).status_code == 422


def test_get_problem_and_404(client, seeded):
    ok = client.get("/api/problems/4/A")
    assert ok.status_code == 200
    assert ok.json()["name"] == "Watermelon"
    assert client.get("/api/problems/4/Q").status_code == 404


def test_tags_endpoint(client, seeded):
    tags = {t["tag"]: t["count"] for t in client.get("/api/problems/tags").json()}
    assert tags["math"] == 2


def test_meta_flags_sample_data(client, seeded):
    assert client.get("/api/meta").json() == {"problem_count": 5, "has_sample_data": False}
