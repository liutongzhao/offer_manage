"""筛选搜索测试：多条件组合 + keyword 模糊 + 标签筛选 + 排序分页。"""
from datetime import date, timedelta

from tests.conftest import envelope


def _seed(client, make_company, make_application):
    """构造已知筛选数据集。"""
    tencent = make_company(name="腾讯")
    bytedance = make_company(name="字节跳动")

    make_application(
        company_id=tencent["id"], type="后端开发", status="已投递",
        channel="内推", city="深圳", position="Go后端工程师",
        apply_date=date(2025, 9, 1).isoformat(),
        notes="重点跟进",
        tag_names=["大厂"],
    )
    make_application(
        company_id=tencent["id"], type="测试开发", status="面试中",
        channel="官网", city="北京", position="测试开发工程师",
        apply_date=date(2025, 10, 10).isoformat(),
    )
    make_application(
        company_id=bytedance["id"], type="AI开发", status="已挂",
        channel="招聘平台", city="上海", position="AI平台工程师",
        apply_date=date(2025, 8, 15).isoformat(),
    )
    return tencent, bytedance


class TestCombinedFilters:
    def test_seed_baseline(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"limit": 50}))
        assert data["total"] == 3

    def test_filter_by_single_status(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"status": "已投递"}))
        assert data["total"] == 1
        assert data["items"][0]["company_name"] == "腾讯"

    def test_filter_by_multi_status_comma(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(
            client.get("/api/v1/applications", params={"status": "已投递,面试中"})
        )
        assert data["total"] == 2

    def test_filter_by_type_and_city_combined(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(
            client.get("/api/v1/applications",
                       params={"type": "后端开发", "city": "深圳"})
        )
        assert data["total"] == 1
        assert data["items"][0]["position"] == "Go后端工程师"

    def test_filter_by_channel(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"channel": "内推"}))
        assert data["total"] == 1

    def test_filter_by_company_id(self, client, make_company, make_application):
        tencent, _ = _seed(client, make_company, make_application)
        data = envelope(
            client.get("/api/v1/applications", params={"company_id": tencent["id"]})
        )
        assert data["total"] == 2

    def test_filter_by_apply_date_range(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(
            client.get(
                "/api/v1/applications",
                params={"apply_date_from": "2025-09-01", "apply_date_to": "2025-09-30"},
            )
        )
        assert data["total"] == 1
        assert data["items"][0]["apply_date"] == "2025-09-01"

    def test_filter_no_match(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"city": "成都"}))
        assert data["total"] == 0
        assert data["items"] == []


class TestKeywordSearch:
    def test_keyword_matches_position(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"keyword": "AI平台"}))
        assert data["total"] == 1
        assert data["items"][0]["company_name"] == "字节跳动"

    def test_keyword_fuzzy_matches_company_name(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"keyword": "字节"}))
        assert data["total"] == 1

    def test_keyword_matches_notes(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"keyword": "重点跟进"}))
        assert data["total"] == 1

    def test_keyword_case_insensitive(self, client, make_company, make_application):
        make_application(position="Python开发", notes="Knows Golang")
        data = envelope(client.get("/api/v1/applications", params={"keyword": "golang"}))
        assert data["total"] == 1


class TestTagFilterAndPagination:
    def test_filter_by_tag(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        data = envelope(client.get("/api/v1/applications", params={"tag": "大厂"}))
        assert data["total"] == 1
        assert "大厂" in data["items"][0]["tag_names"]

    def test_pagination(self, client, make_company, make_application):
        _seed(client, make_company, make_application)
        page1 = envelope(
            client.get("/api/v1/applications", params={"skip": 0, "limit": 2})
        )
        page2 = envelope(
            client.get("/api/v1/applications", params={"skip": 2, "limit": 2})
        )
        assert page1["total"] == 3
        assert len(page1["items"]) == 2
        assert len(page2["items"]) == 1
        ids1 = {i["id"] for i in page1["items"]}
        ids2 = {i["id"] for i in page2["items"]}
        assert ids1.isdisjoint(ids2)

    def test_limit_over_max_422(self, client):
        assert (
            client.get("/api/v1/applications", params={"limit": 500}).status_code == 422
        )
