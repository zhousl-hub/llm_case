# -*- coding: utf-8 -*-
from __future__ import annotations
import sqlite3
import json
import re
from typing import List, Dict, Optional
from config import DB_PATH

STOP_WORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
    "自己", "这", "他", "她", "它", "们", "那", "些", "什么", "怎么", "如何", "哪",
    "为什么", "多少", "几", "可以", "能", "应该", "需要", "情况", "信息", "数据",
    "问题", "关于", "对于", "目前", "现在", "今天", "本周", "本月", "本季度", "今年",
    "最近", "当前", "最新", "如何", "怎样", "是否", "有没有", "能不能",
}


def _extract_keywords(query: str) -> list[str]:
    try:
        import jieba
        words = list(jieba.cut_for_search(query))
        keywords = [w.strip() for w in words if w.strip() and len(w.strip()) > 1 and w.strip() not in STOP_WORDS]
    except ImportError:
        keywords = re.split(r'[\s,，、；;？?！!。.]+', query)
        keywords = [k.strip() for k in keywords if k.strip() and len(k.strip()) > 1]
        keywords = [k for k in keywords if k not in STOP_WORDS]
    if not keywords:
        keywords = [query]
    return keywords


class DatabaseEngine:
    def __init__(self):
        self.db_path = DB_PATH
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_tables(self):
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                email TEXT,
                phone TEXT,
                hire_date TEXT,
                salary REAL,
                status TEXT DEFAULT 'active'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                manager TEXT,
                budget REAL,
                headcount INTEGER,
                location TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT,
                lead TEXT,
                status TEXT,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                type TEXT,
                amount REAL,
                status TEXT,
                sign_date TEXT,
                expire_date TEXT,
                responsible_person TEXT,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                stock INTEGER,
                description TEXT,
                launch_date TEXT
            )
        """)

        self.conn.commit()
        self.close()

    def search(self, query: str, table: str = None, limit: int = 10) -> str:
        self.connect()
        try:
            cursor = self.conn.cursor()
            keywords = _extract_keywords(query)

            if not keywords:
                return json.dumps([], ensure_ascii=False, indent=2, default=str)

            if table and table in ["employees", "departments", "projects", "contracts", "products"]:
                sql = f"SELECT * FROM {table} LIMIT 0"
                cursor.execute(sql)
                columns = [desc[0] for desc in cursor.description]

                conditions = []
                params = []
                for col in columns:
                    for kw in keywords:
                        conditions.append(f"{col} LIKE ?")
                        params.append(f"%{kw}%")

                where_clause = " OR ".join(conditions)
                sql = f"SELECT * FROM {table} WHERE {where_clause} LIMIT ?"
                params.append(limit)

                cursor.execute(sql, params)
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
            else:
                tables = ["employees", "departments", "projects", "contracts", "products"]
                all_results = {}
                for t in tables:
                    sql = f"SELECT * FROM {t} LIMIT 0"
                    cursor.execute(sql)
                    columns = [desc[0] for desc in cursor.description]

                    conditions = []
                    params = []
                    for col in columns:
                        for kw in keywords:
                            conditions.append(f"{col} LIKE ?")
                            params.append(f"%{kw}%")

                    where_clause = " OR ".join(conditions)
                    sql = f"SELECT * FROM {t} WHERE {where_clause} LIMIT ?"
                    params.append(limit)

                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    table_results = [dict(row) for row in rows]
                    if table_results:
                        all_results[t] = table_results

                results = all_results

            return json.dumps(results, ensure_ascii=False, indent=2, default=str)
        finally:
            self.close()

    def execute_sql(self, sql: str) -> str:
        self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            if sql.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                results = [dict(zip(columns, row)) for row in rows]
                return json.dumps(results, ensure_ascii=False, indent=2, default=str)
            else:
                self.conn.commit()
                return json.dumps({"affected_rows": cursor.rowcount}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
        finally:
            self.close()

    def get_schema(self) -> str:
        self.connect()
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            schema_info = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [{"name": col[1], "type": col[2]} for col in cursor.fetchall()]
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                schema_info[table] = {"columns": columns, "row_count": count}

            return json.dumps(schema_info, ensure_ascii=False, indent=2)
        finally:
            self.close()

    def insert_data(self, table: str, data: list[dict]) -> int:
        self.connect()
        try:
            cursor = self.conn.cursor()
            if not data:
                return 0

            columns = list(data[0].keys())
            placeholders = ", ".join(["?"] * len(columns))
            col_str = ", ".join(columns)

            count = 0
            for row in data:
                values = [row.get(col) for col in columns]
                cursor.execute(f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})", values)
                count += 1

            self.conn.commit()
            return count
        finally:
            self.close()
