"""问题记录测试：CRUD、关联投递、分类筛选、PATCH 部分更新。"""
from tests.conftest import envelope


class TestIssueCrud:
    def test_create_and_get(self, client, make_application):
        # Arrange
        app = make_application()
        # Act
        issue = envelope(
            client.post(
                "/api/v1/issues",
                json={
                    "title": "Redis 持久化机制",
                    "category": "面试",
                    "related_application_id": app["id"],
                    "description": "RDB 与 AOF 的区别",
                    "solution": "已梳理笔记",
                    "recorded_date": "2025-10-01",
                },
            )
        )
        got = envelope(client.get(f"/api/v1/issues/{issue['id']}"))
        # Assert
        assert got["title"] == "Redis 持久化机制"
        assert got["related_application_id"] == app["id"]
        assert got["recorded_date"] == "2025-10-01"

    def test_create_default_category(self, client):
        issue = envelope(client.post("/api/v1/issues", json={"title": "泛型擦除"}))
        assert issue["category"] == "其他"

    def test_patch_partial_update(self, client):
        # Arrange
        issue = envelope(
            client.post(
                "/api/v1/issues",
                json={"title": "原题", "category": "技术", "solution": "原解法"},
            )
        )
        # Act：只改 solution
        updated = envelope(
            client.patch(f"/api/v1/issues/{issue['id']}",
                         json={"solution": "新解法", "mastery": "已掌握"})
        )
        # Assert：solution 更新，title/category 保持
        assert updated["solution"] == "新解法"
        assert updated["title"] == "原题"
        assert updated["category"] == "技术"

    def test_delete(self, client):
        issue = envelope(client.post("/api/v1/issues", json={"title": "待删除"}))
        envelope(client.delete(f"/api/v1/issues/{issue['id']}"))
        assert client.get(f"/api/v1/issues/{issue['id']}").status_code == 404

    def test_get_nonexistent_404(self, client):
        assert client.get("/api/v1/issues/99999").status_code == 404


class TestIssueListFilter:
    def test_list_and_filter_by_category(self, client, make_application):
        # Arrange
        app = make_application()
        client.post("/api/v1/issues",
                    json={"title": "A", "category": "面试",
                          "related_application_id": app["id"]})
        client.post("/api/v1/issues", json={"title": "B", "category": "技术"})
        # Act & Assert：按分类
        data = envelope(client.get("/api/v1/issues", params={"category": "技术"}))
        assert [i["title"] for i in data] == ["B"]
        # Act & Assert：按关联投递
        data2 = envelope(
            client.get("/api/v1/issues",
                       params={"related_application_id": app["id"]})
        )
        assert [i["title"] for i in data2] == ["A"]
