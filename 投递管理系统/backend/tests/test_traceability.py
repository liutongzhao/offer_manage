"""溯源闭环测试（最核心，REQ-TRC-001/004/005）：

- PATCH 改多字段 → status_events 逐字段生成，含原值/新值
- 状态变更 event_type 为「状态变更」，其余为「字段变更」
- timeline 接口混排返回正确
"""
from tests.conftest import envelope


def _events_by_field(client, app_id):
    """拉取时间线中 field/status 类事件，按字段名分组。"""
    items = envelope(client.get(f"/api/v1/applications/{app_id}/timeline", params={"limit": 200}))
    return {i["field_name"]: i for i in items if i["kind"] in ("field", "status")}


class TestFieldTraceability:
    def test_patch_multi_fields_creates_one_event_per_field(
        self, client, make_application
    ):
        # Arrange：创建后时间线应有 1 条「创建记录」
        app = make_application(status="待投递", city="北京", salary=None)
        app_id = app["id"]
        before = envelope(client.get(f"/api/v1/applications/{app_id}/timeline"))
        assert len(before) == 1
        assert before[0]["kind"] == "create"

        # Act：一次 PATCH 同时改 4 个字段（含状态）
        resp = client.patch(
            f"/api/v1/applications/{app_id}",
            json={
                "status": "已投递",
                "city": "深圳",
                "salary": "25-40万",
                "notes": "改了备注",
            },
        )
        assert resp.status_code == 200

        # Assert：4 个字段各生成 1 条事件，含原值/新值
        ev = _events_by_field(client, app_id)
        assert ev["当前状态"]["event_type"] == "状态变更"
        assert ev["当前状态"]["old_value"] == "待投递"
        assert ev["当前状态"]["new_value"] == "已投递"
        assert ev["工作城市"]["old_value"] == "北京"
        assert ev["工作城市"]["new_value"] == "深圳"
        assert ev["薪资范围"]["old_value"] is None
        assert ev["薪资范围"]["new_value"] == "25-40万"
        assert ev["备注"]["new_value"] == "改了备注"

    def test_unchanged_field_no_event(self, client, make_application):
        # Arrange
        app = make_application(city="北京", salary="20万")
        # Act：city 传相同值、salary 传新值
        client.patch(
            f"/api/v1/applications/{app['id']}",
            json={"city": "北京", "salary": "30万"},
        )
        # Assert：city 不产生事件
        ev = _events_by_field(client, app["id"])
        assert "工作城市" not in ev
        assert "薪资范围" in ev

    def test_empty_patch_no_events(self, client, make_application):
        # Arrange
        app = make_application()
        before = envelope(client.get(f"/api/v1/applications/{app['id']}/timeline"))
        # Act：空 PATCH（无任何字段变化）
        client.patch(f"/api/v1/applications/{app['id']}", json={})
        # Assert：事件数不变
        after = envelope(client.get(f"/api/v1/applications/{app['id']}/timeline"))
        assert len(after) == len(before)

    def test_date_and_bool_field_events_formatted(self, client, make_application):
        # Arrange
        app = make_application(apply_date=None, deadline=None)
        # Act：改日期字段与布尔字段
        client.patch(
            f"/api/v1/applications/{app['id']}",
            json={"apply_date": "2025-10-12", "archived": True},
        )
        # Assert：日期格式化为 ISO，布尔字段留痕
        ev = _events_by_field(client, app["id"])
        assert ev["投递日期"]["new_value"] == "2025-10-12"
        assert ev["归档状态"]["new_value"] in ("True", "true")

    def test_event_source_recorded(self, client, make_application):
        # Arrange
        app = make_application()
        # Act：带自定义 source 的 PATCH
        client.patch(
            f"/api/v1/applications/{app['id']}?source=代理录入",
            json={"status": "已投递"},
        )
        # Assert：事件来源被记录
        items = envelope(client.get(f"/api/v1/applications/{app['id']}/timeline"))
        status_ev = [i for i in items if i["kind"] == "status"][0]
        assert status_ev["source"] == "代理录入"

    def test_create_with_tag_records_create_event(self, client, make_application):
        # Act
        app = make_application(tag_names=["测试"])
        # Assert：创建事件存在
        items = envelope(client.get(f"/api/v1/applications/{app['id']}/timeline"))
        assert any(i["kind"] == "create" for i in items)


class TestTimeline:
    def test_timeline_mixed_kinds(self, client, make_application):
        # Arrange：创建 → PATCH 状态 → 加沟通记录 → 加链接
        app = make_application()
        client.patch(f"/api/v1/applications/{app['id']}", json={"status": "面试中"})
        client.post(
            f"/api/v1/applications/{app['id']}/communications",
            json={"content": "一面通过", "method": "电话", "contact": "王HR"},
        )
        client.post(
            f"/api/v1/applications/{app['id']}/links",
            json={"url": "https://example.com/jd", "name": "JD"},
        )
        # Act
        items = envelope(client.get(f"/api/v1/applications/{app['id']}/timeline"))
        # Assert：混排包含 status / communication 两类
        kinds = {i["kind"] for i in items}
        assert "create" in kinds
        assert "status" in kinds
        assert "communication" in kinds
        # 沟通记录项携带内容
        comm = [i for i in items if i["kind"] == "communication"][0]
        assert comm["content"] == "一面通过"
        assert comm["contact"] == "王HR"

    def test_timeline_kind_filter(self, client, make_application):
        # Arrange
        app = make_application()
        client.patch(f"/api/v1/applications/{app['id']}", json={"status": "已投递"})
        client.post(
            f"/api/v1/applications/{app['id']}/communications",
            json={"content": "约一面", "method": "邮件"},
        )
        # Act：只看沟通
        comms = envelope(
            client.get(f"/api/v1/applications/{app['id']}/timeline",
                       params={"kind": "communication"})
        )
        # Assert：仅返回沟通类
        assert comms
        assert all(i["kind"] == "communication" for i in comms)

    def test_timeline_nonexistent_app_404(self, client):
        assert (
            client.get("/api/v1/applications/99999/timeline").status_code == 404
        )
