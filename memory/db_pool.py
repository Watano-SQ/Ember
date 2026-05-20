"""
共享 PostgreSQL 连接池

所有需要数据库连接的模块应通过 `get_connection()` 上下文管理器获取连接，
用完自动归还，避免跨线程共享单一连接带来的竞态问题。

用法示例：
    from memory.db_pool import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
"""

import threading
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from pgvector.psycopg2 import register_vector
from config.settings import settings

logger = logging.getLogger(__name__)

# 模块级单例：线程安全的连接池
_pool: pool.ThreadedConnectionPool | None = None
_pool_lock = threading.Lock()


def _get_pool() -> pool.ThreadedConnectionPool:
    """获取或创建全局连接池（线程安全、延迟初始化）"""
    global _pool
    if _pool is not None and not _pool.closed:
        return _pool

    with _pool_lock:
        # double-check
        if _pool is not None and not _pool.closed:
            return _pool

        logger.info("[DBPool] 正在初始化 PostgreSQL 连接池...")
        _pool = pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dbname=settings.PG_DB,
            user=settings.PG_USER,
            password=settings.PG_PASSWORD,
            host=settings.PG_HOST,
            port=settings.PG_PORT,
            connect_timeout=5,
        )
        logger.info("[DBPool] 连接池初始化完成 (min=2, max=10)")
        return _pool


@contextmanager
def get_connection():
    """从连接池借用一个连接，退出上下文时自动归还。

    连接上已注册 pgvector 扩展，可直接使用向量类型。
    如果发生异常会自动 rollback。

    Yields:
        psycopg2 connection
    """
    p = _get_pool()
    conn = p.getconn()
    try:
        # pgvector 注册是 best-effort：DBMemory 等模块不需要向量类型
        try:
            register_vector(conn)
        except Exception:
            pass  # 向量扩展未安装时忽略，不影响普通 SQL 操作
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


def close_pool():
    """关闭连接池（用于优雅退出）"""
    global _pool
    with _pool_lock:
        if _pool is not None and not _pool.closed:
            _pool.closeall()
            logger.info("[DBPool] 连接池已关闭")
            _pool = None
