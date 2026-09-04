"""投递模块测试：CRUD、PATCH 部分更新、参数校验、软删除与恢复、归档。"""
from datetime import date, timedelta

from tests.conftest import envelope

VALID_STATUSES = ["待投递", "已投递", "笔试中", "面试中", "已Offer", "已挂", "已拒绝", "爽约"]


class TestApplicationCreate:
    def test_create_with_defaults(self, client, make_application):
        # Act
        data = make_application()
        # Assert：默认状态待投递、未归档、未删除
        assert data["status"] == "待投递"
        assert data["archived"] is False
        assert data["company_name"]

    def test_create_with_tags_and_fields(self, client, make_application):
        # Act
        data = make_application(
            status="已投递",
            channel="内推",
            city="深圳",
            salary="25-40万",
            apply_date="2025-10-01",
            tag_names=["重点", "大厂"],
        )
        # Assert
        assert sorted(data["tag_names"]) == ["大厂", "重点"]
        assert data["apply_date"] == "2025-10-01"
        assert data["channel"] == "内推"

    def test_create_invalid_type_rejected(self, client, make_company):
        # Act
        resp = client.post(
            "/api/v1/applications",
            json={"company_id": make_company()["id"], "type": "前端开发", "position": "x"},
        )
        # Assert
        assert resp.status_code == 400
        assert "类型" in str(resp.json())

    def test_create_invalid_status_rejected(self, client, make_company):
        resp = client.post(
            "/api/v1/applications",
            json={"company_id": make_company()["id"], "type": "后端开发",
                  "position": "x", "status": "不存在的状态"},
        )
        assert resp.status_code == 400

    def test_create_nonexistent_company_404(self, client):
        resp = client.post(
            "/api/v1/applications",
            json={"company_id": 99999, "type": "后端开发", "position": "x"},
        )
        assert resp.status_code == 404

    def test_create_missing_required_field_422(self, client, make_company):
        # position 缺失 → 参数校验 422
        resp = client.post(
            "/api/v1/applications", json={"company_id": make_company()["id"]}
        )
        assert resp.status_code == 422


class TestApplicationPatchSemantics:
    def test_patch_single_field_keeps_others(self, client, make_application):
        # Arrange
        app = make_application(city="北京", salary="20-30万")
        # Act：只改 status
        data = envelope(
            client.patch(f"/api/v1/applications/{app['id']}",
                         json={"status": "已投递"})
        )
        # Assert：目标字段更新，其余字段保持
        assert data["status"] == "已投递"
        assert data["city"] == "北京"
        assert data["salary"] == "20-30万"

    def test_patch_same_value_is_noop(self, client, make_application):
        # Arrange
        app = make_application(status="已投递")
        # Act：status 传相同值
        data = envelope(
            client.patch(f"/api/v1/applications/{app['id']}",
                         json={"status": "已投递"})
        )
        # Assert：值不变，不应报错
        assert data["status"] == "已投递"

    def test_patch_archived(self, client, make_application):
        app = make_application()
        data = envelope(
            client.patch(f"/api/v1/applications/{app['id']}", json={"archived": True})
        )
        assert data["archived"] is True

    def test_patch_nonexistent_404(self, client):
        assert (
            client.patch("/api/v1/applications/99999", json={"status": "已投递"}).status_code
            == 404
        )

    def test_patch_invalid_status_400(self, client, make_application):
        app = make_application()
        resp = client.patch(
            f"/api/v1/applications/{app['id']}", json={"status": "瞎写的"}
        )
        assert resp.status_code == 400


class TestSoftDeleteAndRestore:
    def test_delete_hides_from_list_restore_brings_back(
        self, client, make_application
    ):
        # Arrange
        app = make_application(position="软删目标岗")
        app_id = app["id"]
        # Act：软删除
        envelope(client.delete(f"/api/v1/applications/{app_id}"))
        # Assert：默认列表不可见
        default_list = envelope(client.get("/api/v1/applications"))
        assert all(i["id"] != app_id for i in default_list["items"])
        # 回收站可见
        trash = envelope(client.get("/api/v1/applications", params={"include_deleted": True}))
        assert any(i["id"] == app_id for i in trash["items"])
        assert trash["total"] == 1
        # Act：恢复
        restored = envelope(client.post(f"/api/v1/applications/{app_id}/restore"))
        # Assert：恢复后默认列表可见
        assert restored["id"] == app_id
        default_list2 = envelope(client.get("/api/v1/applications"))
        assert any(i["id"] == app_id for i in default_list2["items"])

    def test_restore_non_deleted_ok(self, client, make_application):
        # 未删除的记录调 restore 不应报错
        app = make_application()
        data = envelope(client.post(f"/api/v1/applications/{app['id']}/restore"))
        assert data["id"] == app["id"]

    def test_delete_nonexistent_404(self, client):
        assert client.delete("/api/v1/applications/99999").status_code == 404


class TestApplicationListBasics:
    def test_archived_filter(self, client, make_application):
        # Arrange：1 条归档 + 1 条未归档
        a1 = make_application(position="归档岗")
        make_application(position="普通岗")
        client.patch(f"/api/v1/applications/{a1['id']}", json={"archived": True})
        # Act & Assert：默认只看未归档
        default_list = envelope(client.get("/api/v1/applications"))
        assert default_list["total"] == 1
        assert default_list["items"][0]["position"] == "普通岗"
        # archived=true 只看已归档
        archived_list = envelope(client.get("/api/v1/applications", params={"archived": True}))
        assert archived_list["total"] == 1
        assert archived_list["items"][0]["position"] == "归档岗"

    def test_sort_by_deadline(self, client, make_application):
        # Arrange
        make_application(deadline=(date.today() + timedelta(days=10)).isoformat())
        make_application(deadline=(date.today() + timedelta(days=1)).isoformat())
        # Act：按 deadline 升序
        items = envelope(
            client.get("/api/v1/applications",
                       params={"sort_by": "deadline", "order": "asc"})
        )["items"]
        # Assert：deadline 空值排最后/最前不定，但非空值应升序
        deadlines = [i["deadline"] for i in items if i["deadline"]]
        assert deadlines == sorted(deadlines)

    def test_cities_endpoint(self, client, make_application):
        # Arrange
        make_application(city="杭州")
        make_application(city="杭州")
        make_application(city="武汉")
        # Act
        cities = envelope(client.get("/api/v1/applications/cities"))
        # Assert：去重排序
        assert cities == ["杭州", "武汉"]
