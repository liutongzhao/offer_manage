"""链接与标签测试：增删改、失效标记、投递-标签关联（整体替换语义）。"""
from tests.conftest import envelope


class TestLinks:
    def test_create_and_list(self, client, make_application):
        # Arrange
        app = make_application()
        # Act
        link = envelope(
            client.post(
                f"/api/v1/applications/{app['id']}/links",
                json={"url": "https://careers.example.com/123", "name": "投递入口",
                      "link_type": "投递入口"},
            )
        )
        items = envelope(client.get(f"/api/v1/applications/{app['id']}/links"))
        # Assert
        assert link["url"] == "https://careers.example.com/123"
        assert link["is_invalid"] is False
        assert len(items) == 1

    def test_create_empty_url_422(self, client, make_application):
        app = make_application()
        resp = client.post(
            f"/api/v1/applications/{app['id']}/links", json={"url": "   "}
        )
        assert resp.status_code == 422

    def test_create_nonexistent_application_404(self, client):
        resp = client.post(
            "/api/v1/applications/99999/links", json={"url": "https://x.com"}
        )
        assert resp.status_code == 404

    def test_mark_invalid_and_revert(self, client, make_application):
        # Arrange
        app = make_application()
        link = envelope(
            client.post(
                f"/api/v1/applications/{app['id']}/links",
                json={"url": "https://old.example.com"},
            )
        )
        # Act：标记失效
        data = envelope(
            client.patch(f"/api/v1/links/{link['id']}", json={"is_invalid": True})
        )
        # Assert
        assert data["is_invalid"] is True
        # Act：恢复有效
        data2 = envelope(
            client.patch(f"/api/v1/links/{link['id']}", json={"is_invalid": False})
        )
        assert data2["is_invalid"] is False

    def test_delete_link(self, client, make_application):
        app = make_application()
        link = envelope(
            client.post(
                f"/api/v1/applications/{app['id']}/links",
                json={"url": "https://a.com"},
            )
        )
        envelope(client.delete(f"/api/v1/links/{link['id']}"))
        assert envelope(client.get(f"/api/v1/applications/{app['id']}/links")) == []

    def test_patch_nonexistent_link_404(self, client):
        resp = client.patch("/api/v1/links/99999", json={"is_invalid": True})
        assert resp.status_code == 404


class TestTags:
    def test_tag_crud(self, client):
        # Act：创建
        tag = envelope(
            client.post("/api/v1/tags", json={"name": "高优", "scope": "投递"})
        )
        # Assert
        assert tag["name"] == "高优"
        # Act：改名
        updated = envelope(
            client.patch(f"/api/v1/tags/{tag['id']}", json={"name": "最高优"})
        )
        assert updated["name"] == "最高优"
        # Act：删除后列表不含
        envelope(client.delete(f"/api/v1/tags/{tag['id']}"))
        names = [t["name"] for t in envelope(client.get("/api/v1/tags"))]
        assert "最高优" not in names

    def test_create_tag_empty_name_422(self, client):
        assert client.post("/api/v1/tags", json={"name": ""}).status_code == 422

    def test_set_application_tags_replace_semantics(self, client, make_application):
        # Arrange：先打 2 个标签
        app = make_application()
        app_id = app["id"]
        app2 = envelope(
            client.put(f"/api/v1/applications/{app_id}/tags",
                       json={"names": ["大厂", "重点"]})
        )
        assert sorted(app2["tag_names"]) == ["大厂", "重点"]
        # Act：整体替换为 1 个
        replaced = envelope(
            client.put(f"/api/v1/applications/{app_id}/tags", json={"names": ["备用"]})
        )
        # Assert：旧标签被替换
        assert replaced["tag_names"] == ["备用"]
        # Assert：标签自动建档且 usage_count 正确
        tags = {t["name"]: t for t in envelope(client.get("/api/v1/tags"))}
        assert "大厂" in tags
        assert tags["备用"]["usage_count"] == 1
        assert tags["大厂"]["usage_count"] == 0

    def test_set_tags_dedup_and_blank_filtered(self, client, make_application):
        # Arrange
        app = make_application()
        # Act：重复名与空白项
        data = envelope(
            client.put(
                f"/api/v1/applications/{app['id']}/tags",
                json={"names": ["重复", "重复", "  "]},
            )
        )
        # Assert：去重且过滤空白
        assert data["tag_names"] == ["重复"]

    def test_set_tags_nonexistent_application_404(self, client):
        resp = client.put("/api/v1/applications/99999/tags", json={"names": ["x"]})
        assert resp.status_code == 404
