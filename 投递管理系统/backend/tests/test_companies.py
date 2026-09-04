"""公司模块测试：CRUD、PATCH 部分更新语义、同名校验、投递数聚合、404。"""
import pytest

from tests.conftest import envelope


class TestCompanyCreate:
    def test_create_minimal(self, client, make_company):
        # Arrange & Act
        data = make_company(name="字节跳动", city="北京", scale="大厂")
        # Assert
        assert data["name"] == "字节跳动"
        assert data["city"] == "北京"
        assert data["scale"] == "大厂"
        assert data["id"] > 0

    def test_create_duplicate_name_rejected(self, client, make_company):
        # Arrange
        make_company(name="重复公司")
        # Act
        resp = client.post("/api/v1/companies", json={"name": "重复公司"})
        # Assert
        assert resp.status_code == 400
        assert "同名" in str(resp.json())


class TestCompanyListAndCount:
    def test_list_with_application_count(self, client, make_company, make_application):
        # Arrange
        c = make_company(name="计数公司")
        make_application(company_id=c["id"])
        make_application(company_id=c["id"])
        # Act
        items = envelope(client.get("/api/v1/companies", params={"keyword": "计数公司"}))
        # Assert
        assert len(items) == 1
        assert items[0]["application_count"] == 2

    def test_list_without_count(self, client, make_company):
        # Arrange
        make_company(name="无计数公司")
        # Act
        items = envelope(
            client.get("/api/v1/companies", params={"with_count": False})
        )
        # Assert
        assert all("application_count" not in i for i in items)

    def test_list_keyword_searches_alias(self, client, make_company):
        # Arrange
        make_company(name="某某科技", alias="鹅厂")
        # Act
        items = envelope(client.get("/api/v1/companies", params={"keyword": "鹅厂"}))
        # Assert
        assert [i["name"] for i in items] == ["某某科技"]


class TestCompanyUpdate:
    def test_patch_partial_update_keeps_other_fields(self, client, make_company):
        # Arrange
        c = make_company(name="更新公司", city="上海", industry="互联网")
        # Act：只改 city
        data = envelope(
            client.patch(f"/api/v1/companies/{c['id']}", json={"city": "深圳"})
        )
        # Assert：city 更新，industry 保持不变
        assert data["city"] == "深圳"
        assert data["industry"] == "互联网"
        assert data["name"] == "更新公司"

    def test_patch_to_existing_name_rejected(self, client, make_company):
        # Arrange
        make_company(name="甲公司")
        c2 = make_company(name="乙公司")
        # Act
        resp = client.patch(f"/api/v1/companies/{c2['id']}", json={"name": "甲公司"})
        # Assert
        assert resp.status_code == 400


class TestCompanyDeleteAnd404:
    def test_delete_and_404_after(self, client, make_company):
        # Arrange
        c = make_company()
        # Act
        envelope(client.delete(f"/api/v1/companies/{c['id']}"))
        # Assert
        assert client.get(f"/api/v1/companies/{c['id']}").status_code == 404

    def test_get_nonexistent_returns_404(self, client):
        assert client.get("/api/v1/companies/99999").status_code == 404

    def test_patch_nonexistent_returns_404(self, client):
        resp = client.patch("/api/v1/companies/99999", json={"city": "广州"})
        assert resp.status_code == 404
