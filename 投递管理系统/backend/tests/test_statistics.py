"""统计分析测试：summary / funnel / trend / todos（已知数据断言）。"""
from datetime import date, timedelta

from tests.conftest import envelope


class TestSummary:
    def test_summary_with_known_data(self, client, make_application, make_company):
        # Arrange：3 条投递（2 后端 1 测试开发），1 条已Offer，软删 1 条不计入
        make_application(type="后端开发", status="已Offer", channel="内推")
        make_application(type="后端开发", status="面试中", channel="内推")
        make_application(type="测试开发", status="已投递", channel="官网")
        deleted = make_application(type="AI开发", status="已投递")
        client.delete(f"/api/v1/applications/{deleted['id']}")
        # Act
        s = envelope(client.get("/api/v1/analytics/summary"))
        # Assert
        assert s["total"] == 3
        assert s["by_type"] == {"后端开发": 2, "测试开发": 1}
        assert s["by_status"]["已Offer"] == 1
        assert s["by_status"]["面试中"] == 1
        assert s["by_channel"] == {"内推": 2, "官网": 1}
        assert s["offered"] == 1
        assert s["conversion_rate"] == round(1 / 3 * 100, 1)

    def test_summary_empty(self, client):
        s = envelope(client.get("/api/v1/analytics/summary"))
        assert s["total"] == 0
        assert s["conversion_rate"] == 0.0
        assert s["issues_total"] == 0


class TestFunnel:
    def test_funnel_counts_by_status_ladder(self, client, make_application):
        # Arrange：投递环节=5（已投递1+笔试中1+面试中1+已Offer1+已挂1）
        make_application(status="已投递")
        make_application(status="笔试中")
        make_application(status="面试中")
        make_application(status="已Offer")
        make_application(status="已挂")
        # Act
        f = envelope(client.get("/api/v1/analytics/funnel"))
        # Assert
        counts = {st["stage"]: st["count"] for st in f["stages"]}
        assert counts == {"投递": 5, "笔试": 3, "面试": 2, "Offer": 1}
        percents = {st["stage"]: st["percent"] for st in f["stages"]}
        assert percents == {"投递": 100.0, "笔试": 60.0, "面试": 40.0, "Offer": 20.0}

    def test_funnel_pending_not_in_ladder(self, client, make_application):
        # 「待投递」不计入任何环节
        make_application(status="待投递")
        f = envelope(client.get("/api/v1/analytics/funnel"))
        assert all(st["count"] == 0 for st in f["stages"])


class TestTrend:
    def test_trend_monthly_known_counts(self, client, make_application):
        # Arrange：本月 2 条 + 40 天前 1 条（必属上一个月）
        today = date.today()
        make_application(apply_date=today.isoformat())
        make_application(apply_date=today.isoformat())
        make_application(apply_date=(today - timedelta(days=40)).isoformat())
        # Act
        points = envelope(
            client.get("/api/v1/analytics/trend", params={"granularity": "month"})
        )
        # Assert
        this_month = today.strftime("%Y-%m")
        last_month = (today - timedelta(days=40)).strftime("%Y-%m")
        by_period = {p["period"]: p["count"] for p in points}
        assert by_period[this_month] == 2
        assert by_period[last_month] == 1

    def test_trend_excludes_soft_deleted(self, client, make_application):
        app = make_application(apply_date=date.today().isoformat())
        client.delete(f"/api/v1/applications/{app['id']}")
        points = envelope(client.get("/api/v1/analytics/trend"))
        assert all(p["count"] == 0 for p in points) or points == []

    def test_trend_future_date_out_of_window(self, client, make_application):
        # apply_date 在窗口外（>6 个月前 且 本测试只造今天的数据，另外造远未来不影响窗口）
        make_application(apply_date=(date.today() - timedelta(days=400)).isoformat())
        points = envelope(client.get("/api/v1/analytics/trend"))
        assert points == []


class TestTodos:
    def test_todo_groups_expired_due_soon(self, client, make_application):
        # Arrange
        expired = make_application(status="待投递", position="已过期岗",
                                   deadline=(date.today() - timedelta(days=2)).isoformat())
        due = make_application(status="待投递", position="临期岗",
                               deadline=(date.today() + timedelta(days=3)).isoformat())
        # Act
        t = envelope(client.get("/api/v1/analytics/todos"))
        # Assert
        expired_ids = [i["application_id"] for i in t["expired"]]
        due_ids = [i["application_id"] for i in t["due_soon"]]
        assert expired["id"] in expired_ids
        assert due["id"] in due_ids
        exp_item = [i for i in t["expired"] if i["application_id"] == expired["id"]][0]
        assert exp_item["days_left"] == -2

    def test_terminal_status_excluded_from_todos(self, client, make_application):
        # 终态（已挂等）即使 deadline 过期也不进待办
        make_application(status="已挂",
                         deadline=(date.today() - timedelta(days=5)).isoformat())
        t = envelope(client.get("/api/v1/analytics/todos"))
        assert t["expired"] == []
        assert t["due_soon"] == []

    def test_far_deadline_not_in_due_soon(self, client, make_application):
        # 8 天后截止 → 不属于 7 天临期
        make_application(status="待投递",
                         deadline=(date.today() + timedelta(days=8)).isoformat())
        t = envelope(client.get("/api/v1/analytics/todos"))
        assert t["due_soon"] == []


class TestRecentEvents:
    def test_recent_events_shape(self, client, make_application):
        # Arrange
        app = make_application()
        client.patch(f"/api/v1/applications/{app['id']}", json={"status": "已投递"})
        client.post(
            f"/api/v1/applications/{app['id']}/communications",
            json={"content": "聊一下", "method": "微信", "contact": "HR"},
        )
        # Act
        items = envelope(client.get("/api/v1/analytics/recent-events"))
        # Assert：包含事件与沟通两类，字段齐全
        kinds = {i["kind"] for i in items}
        assert "event" in kinds and "communication" in kinds
        for i in items:
            assert {"time", "application_id", "company_name", "summary"} <= set(i)
