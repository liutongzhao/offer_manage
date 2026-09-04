"""沟通记录测试：创建（含自定义过去时间）、列表、PATCH、删除。"""
from datetime import datetime

from tests.conftest import envelope


class TestCommunicationCreate:
    def test_create_with_custom_past_time(self, client, make_application):
        # Arrange
        app = make_application()
        # Act：显式传入过去时间
        data = envelope(
            client.post(
                f"/api/v1/applications/{app['id']}/communications",
                json={
                    "content": "上周电话沟通",
                    "contact": "李HR",
                    "method": "电话",
                    "my_action": "发跟进邮件",
                    "occurred_at": "2025-09-01T10:30:00",
                },
            )
        )
        # Assert：自定义时间被保留（不取当前时间）
        assert data["occurred_at"].startswith("2025-09-01T10:30:00")
        assert data["contact"] == "李HR"
        assert data["my_action"] == "发跟进邮件"

    def test_create_default_time_is_now(self, client, make_application):
        # Arrange
        app = make_application()
        # Act：不传 occurred_at
        data = envelope(
            client.post(
                f"/api/v1/applications/{app['id']}/communications",
                json={"content": "刚聊了聊", "method": "微信"},
            )
        )
        # Assert：自动取当前时间（与系统当前年份一致）
        assert data["occurred_at"] is not None
        assert data["occurred_at"][:4] == str(datetime.now().year)

    def test_create_nonexistent_application_404(self, client):
        resp = client.post(
            "/api/v1/applications/99999/communications",
            json={"content": "x"},
        )
        assert resp.status_code == 404

    def test_create_missing_content_422(self, client, make_application):
        app = make_application()
        resp = client.post(
            f"/api/v1/applications/{app['id']}/communications", json={"method": "邮件"}
        )
        assert resp.status_code == 422


class TestCommunicationListAndMutate:
    def test_list_by_application(self, client, make_application):
        # Arrange：两条沟通
        app = make_application()
        client.post(
            f"/api/v1/applications/{app['id']}/communications",
            json={"content": "第一次", "occurred_at": "2025-09-05T09:00:00"},
        )
        client.post(
            f"/api/v1/applications/{app['id']}/communications",
            json={"content": "第二次", "occurred_at": "2025-09-10T09:00:00"},
        )
        # Act
        items = envelope(
            client.get(f"/api/v1/applications/{app['id']}/communications")
        )
        # Assert
        assert len(items) == 2
        contents = {i["content"] for i in items}
        assert contents == {"第一次", "第二次"}

    def test_patch_partial_update(self, client, make_application):
        # Arrange
        app = make_application()
        c = envelope(
            client.post(
                f"/api/v1/applications/{app['id']}/communications",
                json={"content": "原内容", "method": "邮件", "contact": "张三"},
            )
        )
        # Act：只改 method
        data = envelope(
            client.patch(f"/api/v1/communications/{c['id']}", json={"method": "电话"})
        )
        # Assert：method 更新、content 保持
        assert data["method"] == "电话"
        assert data["content"] == "原内容"

    def test_delete(self, client, make_application):
        # Arrange
        app = make_application()
        c = envelope(
            client.post(
                f"/api/v1/applications/{app['id']}/communications",
                json={"content": "待删除"},
            )
        )
        # Act
        envelope(client.delete(f"/api/v1/communications/{c['id']}"))
        # Assert：列表为空
        items = envelope(
            client.get(f"/api/v1/applications/{app['id']}/communications")
        )
        assert items == []

    def test_patch_nonexistent_404(self, client):
        resp = client.patch("/api/v1/communications/99999", json={"method": "微信"})
        assert resp.status_code == 404
