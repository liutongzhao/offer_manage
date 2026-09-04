"""数据模块测试：CSV 导出（BOM/表头/中文）、导入校验（错误行定位）、备份/恢复（MinIO mock）。"""
import io

import pytest

from tests.conftest import envelope


def _make_csv(rows: list[str], bom: bool = True) -> bytes:
    header = "公司名称,投递类型,岗位名称,当前状态,投递渠道,工作城市,投递日期,截止日期,面试轮次,结果日期,薪资范围,内推人,标签,备注"
    text = header + "\n" + "\n".join(rows) + "\n"
    data = text.encode("utf-8")
    return (b"\xef\xbb\xbf" + data) if bom else data


class TestCsvExport:
    def test_export_has_bom_header_and_chinese(self, client, make_application):
        # Arrange
        make_application(
            city="深圳", salary="25-40万", notes="备注内容",
            tag_names=["大厂", "重点"], status="已投递",
        )
        # Act
        resp = client.get("/api/v1/data/export/applications.csv")
        # Assert
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        raw = resp.content
        assert raw.startswith(b"\xef\xbb\xbf"), "CSV 缺少 UTF-8 BOM"
        text = raw.decode("utf-8-sig")
        lines = text.strip().splitlines()
        assert lines[0].split(",")[0] == "公司名称"
        assert "深圳" in lines[1]
        assert "25-40万" in lines[1]
        assert "大厂、重点" in lines[1]

    def test_export_respects_filter_and_excludes_deleted(
        self, client, make_application
    ):
        # Arrange
        make_application(city="深圳", position="导出岗A")
        make_application(city="北京", position="导出岗B")
        deleted = make_application(city="深圳", position="已删除岗")
        client.delete(f"/api/v1/applications/{deleted['id']}")
        # Act
        resp = client.get("/api/v1/data/export/applications.csv",
                          params={"city": "深圳"})
        # Assert：只导出筛选结果且不含软删除
        text = resp.content.decode("utf-8-sig")
        assert "导出岗A" in text
        assert "导出岗B" not in text
        assert "已删除岗" not in text

    def test_export_empty(self, client):
        resp = client.get("/api/v1/data/export/applications.csv")
        text = resp.content.decode("utf-8-sig")
        assert text.strip().splitlines()[0].startswith("公司名称")


class TestCsvImport:
    def test_import_success_with_auto_company_and_tags(self, client):
        # Arrange
        csv_bytes = _make_csv(
            ["新公司A,后端开发,Go工程师,已投递,内推,深圳,2025-10-01,,,,25-40万,老王,大厂、重点,备注1"]
        )
        # Act
        result = envelope(
            client.post("/api/v1/data/import/applications",
                        files={"file": ("a.csv", io.BytesIO(csv_bytes), "text/csv")})
        )
        # Assert
        assert result["success_count"] == 1
        assert result["fail_count"] == 0
        apps = envelope(client.get("/api/v1/applications", params={"keyword": "新公司A"}))
        assert apps["total"] == 1
        item = apps["items"][0]
        assert sorted(item["tag_names"]) == ["大厂", "重点"]
        assert item["salary"] == "25-40万"

    def test_import_reports_error_rows_with_line_numbers(self, client):
        # Arrange：第 3 行缺必填、第 4 行类型非法、第 5 行状态非法
        csv_bytes = _make_csv(
            [
                "公司A,后端开发,岗位1,,,,",
                ",后端开发,岗位2,,,,",          # 第 3 行：缺公司名
                "公司B,前端开发,岗位3,,,,",      # 第 4 行：类型非法
                "公司C,后端开发,岗位4,瞎状态,,,",  # 第 5 行：状态非法
            ]
        )
        # Act
        result = envelope(
            client.post("/api/v1/data/import/applications",
                        files={"file": ("bad.csv", io.BytesIO(csv_bytes), "text/csv")})
        )
        # Assert
        assert result["success_count"] == 1
        assert result["fail_count"] == 3
        fail_rows = {f["row"] for f in result["failures"]}
        assert fail_rows == {3, 4, 5}
        assert any("公司名称" in f["error"] for f in result["failures"])
        assert any("投递类型" in f["error"] for f in result["failures"])
        assert any("状态" in f["error"] for f in result["failures"])

    def test_import_gbk_encoded_file(self, client):
        # Arrange：GBK 编码（无 BOM）
        header = "公司名称,投递类型,岗位名称"
        row = "GBK公司,后端开发,GBK岗位"
        csv_bytes = (header + "\n" + row + "\n").encode("gbk")
        # Act
        result = envelope(
            client.post("/api/v1/data/import/applications",
                        files={"file": ("gbk.csv", io.BytesIO(csv_bytes), "text/csv")})
        )
        # Assert
        assert result["success_count"] == 1
        apps = envelope(client.get("/api/v1/applications", params={"keyword": "GBK公司"}))
        assert apps["total"] == 1

    def test_import_empty_file_400(self, client):
        resp = client.post(
            "/api/v1/data/import/applications",
            files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
        )
        assert resp.status_code == 400


class TestBackupRestore:
    def test_backup_uploads_to_storage(self, client, monkeypatch):
        # Arrange：mock MinIO 上传
        uploaded = {}

        def fake_upload(key, data, content_type=None):
            uploaded["key"], uploaded["data"] = key, data

        from app.storage import minio_client
        monkeypatch.setattr(minio_client, "upload_file", fake_upload)
        # Act
        info = envelope(client.post("/api/v1/data/backup"))
        # Assert
        assert info["object_key"].startswith("备份/backup-")
        assert info["object_key"].endswith(".db")
        assert uploaded["key"] == info["object_key"]
        assert uploaded["data"][:15] == b"SQLite format 3"

    def test_list_backups_sorted(self, client, monkeypatch):
        # Arrange：mock MinIO 客户端列举
        class FakeObj:
            def __init__(self, name, size):
                self.object_name = name
                self.size = size
                from datetime import datetime
                self.last_modified = datetime(2025, 10, 1)

        class FakeClient:
            def list_objects(self, bucket, prefix, recursive):
                return [
                    FakeObj("备份/backup-20251001-000000.db", 100),
                    FakeObj("备份/backup-20251002-000000.db", 200),
                ]

        from app.storage import minio_client
        monkeypatch.setattr(minio_client, "get_client", lambda: FakeClient())
        # Act
        items = envelope(client.get("/api/v1/data/backups"))
        # Assert：按 object_key 倒序
        keys = [i["object_key"] for i in items]
        assert keys == sorted(keys, reverse=True)
        assert items[0]["object_key"] == "备份/backup-20251002-000000.db"

    def test_restore_roundtrip(self, client, monkeypatch, make_application):
        # Arrange：造数据 → mock 下载返回当前库文件字节
        make_application(position="恢复前存在")
        from app.core.db import DB_PATH
        from app.storage import minio_client
        with open(DB_PATH, "rb") as f:
            db_bytes = f.read()
        monkeypatch.setattr(minio_client, "download_file", lambda key: db_bytes)
        # Act
        result = envelope(
            client.post("/api/v1/data/restore", json={"object_key": "备份/backup-x.db"})
        )
        # Assert
        assert result["restored"] is True
        assert result["object_key"] == "备份/backup-x.db"
        # 清理恢复流程产生的 .bak-before-restore 文件
        import os
        bak = DB_PATH + ".bak-before-restore"
        if os.path.exists(bak):
            os.remove(bak)

    def test_restore_rejects_non_backup_prefix(self, client):
        resp = client.post(
            "/api/v1/data/restore", json={"object_key": "附件/1/x.png"}
        )
        assert resp.status_code == 400

    def test_restore_missing_backup_404(self, client, monkeypatch):
        from app.storage import minio_client

        def boom(key):
            raise Exception("no such object")

        monkeypatch.setattr(minio_client, "download_file", boom)
        resp = client.post(
            "/api/v1/data/restore", json={"object_key": "备份/not-exist.db"}
        )
        assert resp.status_code == 404
