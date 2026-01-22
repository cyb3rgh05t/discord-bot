"""Databases endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sqlite3
import os

router = APIRouter()


class TableInfo(BaseModel):
    database: str
    name: str


class DatabaseStats(BaseModel):
    databases: int
    tables: int
    records: int


class DatabasesResponse(BaseModel):
    tables: List[TableInfo]
    stats: DatabaseStats


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    results: Optional[List[List[Any]]] = None
    message: Optional[str] = None


class ColumnSchema(BaseModel):
    cid: int
    name: str
    type: str
    notnull: bool
    default: Optional[Any]
    pk: bool


class TableDataResponse(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    table_schema: List[ColumnSchema]
    page: int
    per_page: int
    total: int
    database: str


def find_table_database(table_name: str) -> Optional[str]:
    """Find which database contains the specified table"""
    if not os.path.exists("databases"):
        return None

    for db_file in os.listdir("databases"):
        if db_file.endswith(".db"):
            db_name = db_file[:-3]
            try:
                conn = get_db_connection(db_name)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,),
                )
                result = cursor.fetchone()
                conn.close()

                if result:
                    return db_name
            except Exception:
                continue

    return None


def get_db_connection(db_name: str):
    """Get database connection"""
    db_path = os.path.join("databases", f"{db_name}.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail=f"Database '{db_name}' not found")
    return sqlite3.connect(db_path)


def get_database_tables() -> List[TableInfo]:
    """Get list of all tables in databases"""
    tables = []

    if not os.path.exists("databases"):
        return tables

    for db_file in os.listdir("databases"):
        if db_file.endswith(".db"):
            db_name = db_file[:-3]
            try:
                conn = get_db_connection(db_name)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

                for row in cursor.fetchall():
                    tables.append(TableInfo(database=db_name, name=row[0]))

                conn.close()
            except Exception:
                continue

    return tables


@router.get("/", response_model=DatabasesResponse)
async def get_databases():
    """Get database information and statistics"""
    tables = get_database_tables()

    # Calculate statistics
    databases = set()
    total_records = 0

    for table in tables:
        databases.add(table.database)
        # Get record count for each table
        try:
            conn = get_db_connection(table.database)
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table.name}")
            count = cursor.fetchone()[0]
            total_records += count
            conn.close()
        except Exception:
            pass

    stats = DatabaseStats(
        databases=len(databases), tables=len(tables), records=total_records
    )

    return DatabasesResponse(tables=tables, stats=stats)


@router.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    """Execute custom SQL query (read-only)"""
    try:
        query = request.query.strip()

        # Only allow SELECT queries for safety
        if not query.upper().startswith("SELECT"):
            return QueryResponse(
                success=False,
                message="Only SELECT queries are allowed for safety reasons",
            )

        # Try to find which database contains the queried table
        # For simplicity, we'll try each database
        results = None
        last_error = None

        if os.path.exists("databases"):
            for db_file in os.listdir("databases"):
                if db_file.endswith(".db"):
                    db_name = db_file[:-3]
                    try:
                        conn = get_db_connection(db_name)
                        cursor = conn.cursor()
                        cursor.execute(query)
                        results = cursor.fetchall()
                        conn.close()
                        break  # Success, use this result
                    except sqlite3.OperationalError as e:
                        last_error = str(e)
                        continue  # Try next database
                    except Exception as e:
                        last_error = str(e)
                        continue

        if results is not None:
            # Convert tuples to lists for JSON serialization
            results_list = [list(row) for row in results]
            return QueryResponse(success=True, results=results_list)
        else:
            return QueryResponse(
                success=False,
                message=last_error or "No database contains the queried table",
            )

    except Exception as e:
        return QueryResponse(success=False, message=str(e))


@router.get("/table/{table_name}", response_model=TableDataResponse)
async def get_table_data(table_name: str, page: int = 1, per_page: int = 50):
    """Get data from a specific table with pagination"""
    # Validate table name (prevent SQL injection)
    if not table_name.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail=f"Invalid table name: {table_name}")

    # Find which database contains this table
    db_name = find_table_database(table_name)

    if not db_name:
        raise HTTPException(
            status_code=404, detail=f"Table '{table_name}' not found in any database"
        )

    try:
        conn = get_db_connection(db_name)
        cursor = conn.cursor()

        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]

        # Get paginated data
        offset = (page - 1) * per_page
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}")

        columns = [description[0] for description in cursor.description]
        rows = [list(row) for row in cursor.fetchall()]

        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema_raw = cursor.fetchall()

        schema = [
            ColumnSchema(
                cid=col[0],
                name=col[1],
                type=col[2],
                notnull=bool(col[3]),
                default=col[4],
                pk=bool(col[5]),
            )
            for col in schema_raw
        ]

        conn.close()

        return TableDataResponse(
            columns=columns,
            rows=rows,
            table_schema=schema,
            page=page,
            per_page=per_page,
            total=total_count,
            database=db_name,
        )

    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error accessing table '{table_name}': {str(e)}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
