# flake8: noqa: E501, W291
import sqlite3
from datetime import datetime

import pandas as pd


class DBManager:
    """
    SQLite Database Manager for NeuraFlow Analytics.
    Handles logging and retrieving metrics for the Analytics Dashboard.
    """

    def __init__(self, db_path="analytics.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Documents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    pages INTEGER,
                    chunks INTEGER,
                    file_size INTEGER,
                    upload_time DATETIME
                )
            """)

            # Queries Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT,
                    latency REAL,
                    rag_time REAL,
                    similarity_score REAL,
                    fallback_used BOOLEAN,
                    timestamp DATETIME,
                    memory_hit BOOLEAN DEFAULT 0,
                    memory_tokens INTEGER DEFAULT 0,
                    chat_turns INTEGER DEFAULT 0,
                    first_token_time REAL DEFAULT 0.0,
                    tokens_per_sec REAL DEFAULT 0.0
                )
            """)

            # Schema Evolution (if table already existed before memory update)
            try:
                cursor.execute(
                    "ALTER TABLE queries ADD COLUMN memory_hit BOOLEAN DEFAULT 0"
                )
                cursor.execute(
                    "ALTER TABLE queries ADD COLUMN memory_tokens INTEGER DEFAULT 0"
                )
                cursor.execute(
                    "ALTER TABLE queries ADD COLUMN chat_turns INTEGER DEFAULT 0"
                )
            except sqlite3.OperationalError:
                pass

            try:
                cursor.execute(
                    "ALTER TABLE queries ADD COLUMN first_token_time REAL DEFAULT 0.0"
                )
                cursor.execute(
                    "ALTER TABLE queries ADD COLUMN tokens_per_sec REAL DEFAULT 0.0"
                )
            except sqlite3.OperationalError:
                pass

            # Provider Reliability Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS provider_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_name TEXT,
                    success BOOLEAN,
                    error_msg TEXT,
                    response_time REAL,
                    timestamp DATETIME
                )
            """)

            # Web Searches Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    provider_used TEXT,
                    fallback_used BOOLEAN,
                    search_time REAL,
                    results_count INTEGER,
                    timestamp DATETIME
                )
            """)
            conn.commit()

    def log_document(self, filename: str, pages: int, chunks: int, file_size: int):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO documents (filename, pages, chunks, file_size, upload_time) VALUES (?, ?, ?, ?, ?)",
                (filename, pages, chunks, file_size, datetime.now()),
            )

    def log_query(
        self,
        provider: str,
        latency: float,
        rag_time: float,
        similarity_score: float,
        fallback_used: bool,
        memory_hit: bool = False,
        memory_tokens: int = 0,
        chat_turns: int = 0,
        first_token_time: float = 0.0,
        tokens_per_sec: float = 0.0,
    ):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO queries (provider, latency, rag_time, similarity_score, fallback_used, timestamp, memory_hit, memory_tokens, chat_turns, first_token_time, tokens_per_sec) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    provider,
                    latency,
                    rag_time,
                    similarity_score,
                    fallback_used,
                    datetime.now(),
                    memory_hit,
                    memory_tokens,
                    chat_turns,
                    first_token_time,
                    tokens_per_sec,
                ),
            )

    def log_provider(
        self, provider_name: str, success: bool, error_msg: str, response_time: float
    ):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO provider_logs (provider_name, success, error_msg, response_time, timestamp) VALUES (?, ?, ?, ?, ?)",
                (provider_name, success, error_msg, response_time, datetime.now()),
            )

    # --- Analytics Retrieval Methods ---

    def get_total_queries(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute("SELECT COUNT(*) FROM queries").fetchone()
            return res[0] if res else 0

    def get_average_latency(self) -> float:
        with self._get_connection() as conn:
            res = conn.execute("SELECT AVG(latency) FROM queries").fetchone()
            return res[0] if res and res[0] else 0.0

    def get_documents_indexed(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
            return res[0] if res else 0

    def get_total_chunks(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute("SELECT SUM(chunks) FROM documents").fetchone()
            return res[0] if res and res[0] else 0

    def get_average_similarity(self) -> float:
        with self._get_connection() as conn:
            res = conn.execute("SELECT AVG(similarity_score) FROM queries").fetchone()
            return res[0] if res and res[0] else 0.0

    def get_fallback_rate(self) -> float:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM queries").fetchone()[0]
            if total == 0:
                return 0.0
            fallbacks = conn.execute(
                "SELECT COUNT(*) FROM queries WHERE fallback_used = 1"
            ).fetchone()[0]
            return (fallbacks / total) * 100

    def get_provider_availability(self) -> float:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM provider_logs").fetchone()[0]
            if total == 0:
                return 100.0
            successes = conn.execute(
                "SELECT COUNT(*) FROM provider_logs WHERE success = 1"
            ).fetchone()[0]
            return (successes / total) * 100

    def get_memory_stats(self):
        with self._get_connection() as conn:
            total_queries = conn.execute("SELECT COUNT(*) FROM queries").fetchone()[0]
            if total_queries == 0:
                return 0, 0, 0.0

            memory_hits = conn.execute(
                "SELECT COUNT(*) FROM queries WHERE memory_hit = 1"
            ).fetchone()[0]
            avg_tokens = conn.execute(
                "SELECT AVG(memory_tokens) FROM queries WHERE memory_hit = 1"
            ).fetchone()[0]
            avg_turns = conn.execute(
                "SELECT AVG(chat_turns) FROM queries WHERE memory_hit = 1"
            ).fetchone()[0]

            return (
                memory_hits,
                int(avg_tokens) if avg_tokens else 0,
                round(avg_turns, 1) if avg_turns else 0.0,
            )

    def get_streaming_stats(self):
        with self._get_connection() as conn:
            avg_first_token = conn.execute(
                "SELECT AVG(first_token_time) FROM queries WHERE first_token_time > 0"
            ).fetchone()[0]
            avg_tps = conn.execute(
                "SELECT AVG(tokens_per_sec) FROM queries WHERE tokens_per_sec > 0"
            ).fetchone()[0]

            # success rate implies where stream actually yielded tokens successfully
            total = conn.execute("SELECT COUNT(*) FROM queries").fetchone()[0]
            successes = conn.execute(
                "SELECT COUNT(*) FROM queries WHERE tokens_per_sec > 0"
            ).fetchone()[0]
            success_rate = (successes / total * 100) if total > 0 else 0.0

            return (
                round(avg_first_token, 2) if avg_first_token else 0.0,
                round(avg_tps, 1) if avg_tps else 0.0,
                round(success_rate, 1),
            )

    # DataFrames for Plotly Charts

    def get_provider_usage_df(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql_query(
                "SELECT provider, COUNT(*) as count FROM queries GROUP BY provider ORDER BY count DESC",
                conn,
            )

    def get_query_volume_df(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            # Group by day
            query = """
                SELECT date(timestamp) as date, COUNT(*) as count 
                FROM queries 
                GROUP BY date(timestamp) 
                ORDER BY date ASC
            """
            return pd.read_sql_query(query, conn)

    def get_latency_comparison_df(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql_query(
                "SELECT provider, AVG(latency) as avg_latency FROM queries GROUP BY provider",
                conn,
            )

    def get_rag_performance_df(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql_query("SELECT rag_time FROM queries", conn)

    # --- Search Analytics Methods ---

    def log_search(
        self,
        query: str,
        provider_used: str,
        fallback_used: bool,
        search_time: float,
        results_count: int,
    ):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO searches (query, provider_used, fallback_used, search_time, results_count, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    query,
                    provider_used,
                    fallback_used,
                    search_time,
                    results_count,
                    datetime.now(),
                ),
            )

    def get_total_searches(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute("SELECT COUNT(*) FROM searches").fetchone()
            return res[0] if res else 0

    def get_average_search_time(self) -> float:
        with self._get_connection() as conn:
            res = conn.execute("SELECT AVG(search_time) FROM searches").fetchone()
            return res[0] if res and res[0] else 0.0

    def get_tavily_searches(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute(
                "SELECT COUNT(*) FROM searches WHERE provider_used = 'Tavily'"
            ).fetchone()
            return res[0] if res else 0

    def get_ddg_searches(self) -> int:
        with self._get_connection() as conn:
            res = conn.execute(
                "SELECT COUNT(*) FROM searches WHERE provider_used = 'DuckDuckGo'"
            ).fetchone()
            return res[0] if res else 0

    def get_search_fallback_rate(self) -> float:
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM searches").fetchone()[0]
            if total == 0:
                return 0.0
            fallbacks = conn.execute(
                "SELECT COUNT(*) FROM searches WHERE fallback_used = 1"
            ).fetchone()[0]
            return (fallbacks / total) * 100

    def get_search_provider_usage_df(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql_query(
                "SELECT provider_used as provider, COUNT(*) as count FROM searches GROUP BY provider_used ORDER BY count DESC",
                conn,
            )

    def get_search_performance_df(self) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql_query(
                "SELECT provider_used as provider, AVG(search_time) as avg_search_time FROM searches GROUP BY provider_used",
                conn,
            )
