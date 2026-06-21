"""
NanoCorp v5.0 - Persistence Layer

Production-grade database abstraction for state persistence.
Supports PostgreSQL, SQLite (for dev), with Redis caching layer.
"""
from __future__ import annotations

import json
import asyncio
from typing import Dict, List, Optional, Any, TypeVar, Generic
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import uuid

try:
    import asyncpg  # PostgreSQL async driver
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    asyncpg = None

try:
    import aiosqlite  # SQLite async driver
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False
    aiosqlite = None

try:
    import redis.asyncio as aioredis  # Redis async driver
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None


# ===========================================
# DATABASE CONFIGURATION
# ===========================================

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: str = "sqlite"  # sqlite, postgres
    host: str = "localhost"
    port: int = 5432
    database: str = "nanocorp"
    username: str = "nanocorp"
    password: str = ""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    pool_size: int = 10
    cache_ttl: int = 300  # seconds


# ===========================================
# BASE REPOSITORY PATTERN
# ===========================================

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository for CRUD operations"""
    
    def __init__(self, db: 'Database', table_name: str):
        self.db = db
        self.table_name = table_name
    
    async def create(self, entity: T) -> str:
        """Create entity, return ID"""
        raise NotImplementedError
    
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        raise NotImplementedError
    
    async def list_all(self, filters: Optional[Dict] = None) -> List[T]:
        """List all entities with optional filters"""
        raise NotImplementedError
    
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """Update entity"""
        raise NotImplementedError
    
    async def delete(self, entity_id: str) -> bool:
        """Delete entity"""
        raise NotImplementedError


# ===========================================
# DATABASE CONNECTION MANAGER
# ===========================================

class Database:
    """
    Main database connection manager with connection pooling.
    Supports PostgreSQL (production) and SQLite (development).
    """
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self._pool = None
        self._conn = None
        self._redis = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
        
        if self.config.db_type == "postgres":
            if not POSTGRES_AVAILABLE:
                raise ImportError("asyncpg required for PostgreSQL. Install: pip install asyncpg")
            
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=5,
                max_size=self.config.pool_size
            )
            
            # Create tables
            await self._create_tables_postgres()
        
        elif self.config.db_type == "sqlite":
            if not SQLITE_AVAILABLE:
                raise ImportError("aiosqlite required for SQLite. Install: pip install aiosqlite")
            
            self._conn = await aiosqlite.connect(f"{self.config.database}.db")
            self._conn.row_factory = aiosqlite.Row
            await self._create_tables_sqlite()
        
        # Initialize Redis cache if available
        if REDIS_AVAILABLE:
            try:
                self._redis = await aioredis.from_url(
                    f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}",
                    decode_responses=True
                )
            except Exception as e:
                print(f"Redis connection failed: {e}")
        
        self._initialized = True
    
    async def _create_tables_postgres(self):
        """Create PostgreSQL tables"""
        async with self._pool.acquire() as conn:
            # Goals table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id TEXT PRIMARY KEY,
                    objective TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'active',
                    deadline TIMESTAMP,
                    success_criteria TEXT,
                    key_results JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Tasks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    task_type TEXT DEFAULT 'general',
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    assigned_worker TEXT,
                    dependencies JSONB,
                    goal_id TEXT REFERENCES goals(id),
                    result JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                )
            """)
            
            # Agents/Workers table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    status TEXT DEFAULT 'idle',
                    current_task_id TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Execution results table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_results (
                    id TEXT PRIMARY KEY,
                    task_id TEXT REFERENCES tasks(id),
                    success BOOLEAN,
                    output JSONB,
                    duration FLOAT,
                    artifacts JSONB,
                    errors JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Memory/events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    agent_id TEXT,
                    data JSONB,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_goal ON tasks(goal_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
    
    async def _create_tables_sqlite(self):
        """Create SQLite tables"""
        # Goals table
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                objective TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'active',
                deadline TEXT,
                success_criteria TEXT,
                key_results TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tasks table
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                task_type TEXT DEFAULT 'general',
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                assigned_worker TEXT,
                dependencies TEXT,
                goal_id TEXT REFERENCES goals(id),
                result TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        """)
        
        # Agents table
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                status TEXT DEFAULT 'idle',
                current_task_id TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Execution results
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_results (
                id TEXT PRIMARY KEY,
                task_id TEXT REFERENCES tasks(id),
                success INTEGER,
                output TEXT,
                duration REAL,
                artifacts TEXT,
                errors TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Events
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                agent_id TEXT,
                data TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self._conn.commit()
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire database connection"""
        if not self._initialized:
            await self.initialize()
        
        if self.config.db_type == "postgres":
            async with self._pool.acquire() as conn:
                yield conn
        else:
            yield self._conn
    
    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cache value"""
        if not self._redis:
            return
        
        ttl = ttl or self.config.cache_ttl
        await self._redis.setex(key, ttl, json.dumps(value))
    
    async def cache_get(self, key: str, default: Any = None):
        """Get cache value"""
        if not self._redis:
            return default
        
        value = await self._redis.get(key)
        if value is None:
            return default
        return json.loads(value)
    
    async def cache_delete(self, key: str):
        """Delete cache key"""
        if not self._redis:
            return
        await self._redis.delete(key)
    
    async def close(self):
        """Close database connections"""
        if self._pool:
            await self._pool.close()
        if self._conn:
            await self._conn.close()
        if self._redis:
            await self._redis.close()


# ===========================================
# ENTITY REPOSITORIES
# ===========================================

@dataclass
class GoalEntity:
    """Goal entity for database"""
    id: str
    objective: str
    priority: str = "medium"
    status: str = "active"
    deadline: Optional[str] = None
    success_criteria: Optional[str] = None
    key_results: List[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GoalRepository(BaseRepository[GoalEntity]):
    """Repository for goal operations"""
    
    def __init__(self, db: Database):
        super().__init__(db, "goals")
    
    async def create(self, entity: GoalEntity) -> str:
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                await conn.execute("""
                    INSERT INTO goals (id, objective, priority, status, deadline, success_criteria, key_results)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, entity.id, entity.objective, entity.priority, entity.status,
                   entity.deadline, entity.success_criteria, json.dumps(entity.key_results or []))
            else:
                await conn.execute("""
                    INSERT INTO goals (id, objective, priority, status, deadline, success_criteria, key_results)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, entity.id, entity.objective, entity.priority, entity.status,
                   entity.deadline, entity.success_criteria, json.dumps(entity.key_results or []))
                await conn.commit()
        
        await self.db.cache_delete("goals:all")
        return entity.id
    
    async def get_by_id(self, entity_id: str) -> Optional[GoalEntity]:
        # Check cache first
        cached = await self.db.cache_get(f"goal:{entity_id}")
        if cached:
            return GoalEntity(**cached)
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                row = await conn.fetchrow("SELECT * FROM goals WHERE id = $1", entity_id)
            else:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("SELECT * FROM goals WHERE id = ?", (entity_id,)) as cursor:
                    row = await cursor.fetchone()
        
        if row:
            entity = GoalEntity(
                id=row["id"],
                objective=row["objective"],
                priority=row["priority"],
                status=row["status"],
                deadline=row["deadline"],
                success_criteria=row["success_criteria"],
                key_results=json.loads(row["key_results"]) if row["key_results"] else [],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            await self.db.cache_set(f"goal:{entity_id}", asdict(entity))
            return entity
        return None
    
    async def list_all(self, filters: Optional[Dict] = None) -> List[GoalEntity]:
        # Check cache
        cache_key = f"goals:{json.dumps(filters, sort_keys=True)}" if filters else "goals:all"
        cached = await self.db.cache_get(cache_key)
        if cached:
            return [GoalEntity(**g) for g in cached]
        
        query = "SELECT * FROM goals"
        params = []
        conditions = []
        
        if filters:
            if "status" in filters:
                conditions.append("status = ?" if self.db.config.db_type == "sqlite" else "status = $1")
                params.append(filters["status"])
            if "priority" in filters:
                conditions.append("priority = ?" if self.db.config.db_type == "sqlite" else "priority = $2")
                params.append(filters["priority"])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                rows = await conn.fetch(query, *params) if params else await conn.fetch(query)
            else:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(query, params) if params else conn.execute(query) as cursor:
                    rows = await cursor.fetchall()
        
        entities = [
            GoalEntity(
                id=row["id"],
                objective=row["objective"],
                priority=row["priority"],
                status=row["status"],
                deadline=row["deadline"],
                success_criteria=row["success_criteria"],
                key_results=json.loads(row["key_results"]) if row["key_results"] else [],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            for row in rows
        ]
        
        await self.db.cache_set(cache_key, [asdict(e) for e in entities])
        return entities
    
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        set_clauses = []
        params = []
        param_idx = 1
        
        for key, value in updates.items():
            if self.db.config.db_type == "postgres":
                set_clauses.append(f"{key} = ${param_idx}")
            else:
                set_clauses.append(f"{key} = ?")
            params.append(json.dumps(value) if isinstance(value, (list, dict)) else value)
            param_idx += 1
        
        set_clauses.append(f"updated_at = {'$' + str(param_idx) if self.db.config.db_type == 'postgres' else '?'}")
        params.append(datetime.now().isoformat())
        
        query = f"UPDATE goals SET {', '.join(set_clauses)} WHERE id = {'$' + str(param_idx + 1) if self.db.config.db_type == 'postgres' else '?'}"
        params.append(entity_id)
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                result = await conn.execute(query, *params)
                updated = result.split()[-1] != "0"
            else:
                await conn.execute(query, params)
                await conn.commit()
                updated = True
        
        await self.db.cache_delete(f"goal:{entity_id}")
        await self.db.cache_delete("goals:all")
        return updated
    
    async def delete(self, entity_id: str) -> bool:
        query = "DELETE FROM goals WHERE id = $1" if self.db.config.db_type == "postgres" else "DELETE FROM goals WHERE id = ?"
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                result = await conn.execute(query, entity_id)
                deleted = result.split()[-1] != "0"
            else:
                await conn.execute(query, (entity_id,))
                await conn.commit()
                deleted = True
        
        await self.db.cache_delete(f"goal:{entity_id}")
        await self.db.cache_delete("goals:all")
        return deleted


@dataclass
class TaskEntity:
    """Task entity for database"""
    id: str
    title: str
    description: Optional[str] = None
    task_type: str = "general"
    priority: str = "medium"
    status: str = "pending"
    assigned_worker: Optional[str] = None
    dependencies: List[str] = None
    goal_id: Optional[str] = None
    result: Optional[Dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None


class TaskRepository(BaseRepository[TaskEntity]):
    """Repository for task operations"""
    
    def __init__(self, db: Database):
        super().__init__(db, "tasks")
    
    async def create(self, entity: TaskEntity) -> str:
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                await conn.execute("""
                    INSERT INTO tasks (id, title, description, task_type, priority, status, assigned_worker, dependencies, goal_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, entity.id, entity.title, entity.description, entity.task_type,
                   entity.priority, entity.status, entity.assigned_worker,
                   json.dumps(entity.dependencies or []), entity.goal_id)
            else:
                await conn.execute("""
                    INSERT INTO tasks (id, title, description, task_type, priority, status, assigned_worker, dependencies, goal_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, entity.id, entity.title, entity.description, entity.task_type,
                   entity.priority, entity.status, entity.assigned_worker,
                   json.dumps(entity.dependencies or []), entity.goal_id)
                await conn.commit()
        
        await self.db.cache_delete(f"tasks:goal:{entity.goal_id}")
        return entity.id
    
    async def get_by_id(self, entity_id: str) -> Optional[TaskEntity]:
        cached = await self.db.cache_get(f"task:{entity_id}")
        if cached:
            return TaskEntity(**cached)
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                row = await conn.fetchrow("SELECT * FROM tasks WHERE id = $1", entity_id)
            else:
                conn.row_factory = aiosqlite.Row
                async with conn.execute("SELECT * FROM tasks WHERE id = ?", (entity_id,)) as cursor:
                    row = await cursor.fetchone()
        
        if row:
            return TaskEntity(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                task_type=row["task_type"],
                priority=row["priority"],
                status=row["status"],
                assigned_worker=row["assigned_worker"],
                dependencies=json.loads(row["dependencies"]) if row["dependencies"] else [],
                goal_id=row["goal_id"],
                result=json.loads(row["result"]) if row["result"] else None,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                completed_at=row["completed_at"]
            )
        return None
    
    async def list_all(self, filters: Optional[Dict] = None) -> List[TaskEntity]:
        cache_key = f"tasks:{json.dumps(filters, sort_keys=True)}" if filters else "tasks:all"
        cached = await self.db.cache_get(cache_key)
        if cached:
            return [TaskEntity(**t) for t in cached]
        
        query = "SELECT * FROM tasks"
        params = []
        conditions = []
        param_idx = 1
        
        if filters:
            if "status" in filters:
                conditions.append(f"status = ${param_idx}" if self.db.config.db_type == "postgres" else "status = ?")
                params.append(filters["status"])
                param_idx += 1
            if "goal_id" in filters:
                conditions.append(f"goal_id = ${param_idx}" if self.db.config.db_type == "postgres" else "goal_id = ?")
                params.append(filters["goal_id"])
                param_idx += 1
            if "assigned_worker" in filters:
                conditions.append(f"assigned_worker = ${param_idx}" if self.db.config.db_type == "postgres" else "assigned_worker = ?")
                params.append(filters["assigned_worker"])
                param_idx += 1
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                rows = await conn.fetch(query, *params) if params else await conn.fetch(query)
            else:
                conn.row_factory = aiosqlite.Row
                async with conn.execute(query, params) if params else conn.execute(query) as cursor:
                    rows = await cursor.fetchall()
        
        entities = [
            TaskEntity(
                id=row["id"],
                title=row["title"],
                description=row["description"],
                task_type=row["task_type"],
                priority=row["priority"],
                status=row["status"],
                assigned_worker=row["assigned_worker"],
                dependencies=json.loads(row["dependencies"]) if row["dependencies"] else [],
                goal_id=row["goal_id"],
                result=json.loads(row["result"]) if row["result"] else None,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                completed_at=row["completed_at"]
            )
            for row in rows
        ]
        
        await self.db.cache_set(cache_key, [asdict(e) for e in entities])
        return entities
    
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        set_clauses = []
        params = []
        param_idx = 1
        
        for key, value in updates.items():
            if self.db.config.db_type == "postgres":
                set_clauses.append(f"{key} = ${param_idx}")
            else:
                set_clauses.append(f"{key} = ?")
            params.append(json.dumps(value) if isinstance(value, (list, dict)) else value)
            param_idx += 1
        
        set_clauses.append(f"updated_at = {'$' + str(param_idx) if self.db.config.db_type == 'postgres' else '?'}")
        params.append(datetime.now().isoformat())
        
        query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = {'$' + str(param_idx + 1) if self.db.config.db_type == 'postgres' else '?'}"
        params.append(entity_id)
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                result = await conn.execute(query, *params)
                updated = result.split()[-1] != "0"
            else:
                await conn.execute(query, params)
                await conn.commit()
                updated = True
        
        await self.db.cache_delete(f"task:{entity_id}")
        return updated
    
    async def delete(self, entity_id: str) -> bool:
        query = "DELETE FROM tasks WHERE id = $1" if self.db.config.db_type == "postgres" else "DELETE FROM tasks WHERE id = ?"
        
        async with self.db.acquire() as conn:
            if self.db.config.db_type == "postgres":
                result = await conn.execute(query, entity_id)
                deleted = result.split()[-1] != "0"
            else:
                await conn.execute(query, (entity_id,))
                await conn.commit()
                deleted = True
        
        await self.db.cache_delete(f"task:{entity_id}")
        return deleted


# ===========================================
# DATABASE FACTORY
# ===========================================

def create_database(config: Optional[DatabaseConfig] = None) -> Database:
    """Create database instance from environment or config"""
    import os
    
    if not config:
        db_type = os.getenv("DATABASE_TYPE", "sqlite")
        config = DatabaseConfig(
            db_type=db_type,
            host=os.getenv("DATABASE_HOST", "localhost"),
            port=int(os.getenv("DATABASE_PORT", "5432")),
            database=os.getenv("DATABASE_NAME", "nanocorp"),
            username=os.getenv("DATABASE_USER", "nanocorp"),
            password=os.getenv("DATABASE_PASSWORD", ""),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379"))
        )
    
    return Database(config)


# ===========================================
# UNIT OF WORK PATTERN
# ===========================================

class UnitOfWork:
    """Unit of Work for transactional operations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.goals: Optional[GoalRepository] = None
        self.tasks: Optional[TaskRepository] = None
    
    async def __aenter__(self):
        await self.db.initialize()
        self.goals = GoalRepository(self.db)
        self.tasks = TaskRepository(self.db)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass  # Connection pooling handles cleanup
