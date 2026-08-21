import sqlite3
from datetime import datetime


DB = "users.db"


def init_projects_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_type TEXT NOT NULL,
            business_name TEXT,
            description TEXT,
            status TEXT DEFAULT 'COLLECTING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_value TEXT,
            required INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
    """)

    conn.commit()
    conn.close()


def create_project(
    user_id,
    project_type,
    business_name=None,
    description=None
):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO projects
        (
            user_id,
            project_type,
            business_name,
            description,
            status
        )
        VALUES (?, ?, ?, ?, 'COLLECTING')
    """, (
        user_id,
        project_type,
        business_name,
        description
    ))

    project_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return project_id


def add_project_field(
    project_id,
    field_name,
    field_value=None,
    required=False
):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO project_fields
        (
            project_id,
            field_name,
            field_value,
            required,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        project_id,
        field_name,
        field_value,
        1 if required else 0,
        "COMPLETE" if field_value else "PENDING"
    ))

    conn.commit()
    conn.close()


def update_project_field(
    project_id,
    field_name,
    field_value
):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM project_fields
        WHERE project_id = ?
        AND field_name = ?
    """, (
        project_id,
        field_name
    ))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE project_fields
            SET field_value = ?,
                status = 'COMPLETE'
            WHERE id = ?
        """, (
            field_value,
            existing[0]
        ))
    else:
        cursor.execute("""
            INSERT INTO project_fields
            (
                project_id,
                field_name,
                field_value,
                status
            )
            VALUES (?, ?, ?, 'COMPLETE')
        """, (
            project_id,
            field_name,
            field_value
        ))

    cursor.execute("""
        UPDATE projects
        SET updated_at = ?
        WHERE id = ?
    """, (
        datetime.now().isoformat(),
        project_id
    ))

    conn.commit()
    conn.close()


def get_project(project_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            user_id,
            project_type,
            business_name,
            description,
            status,
            created_at,
            updated_at
        FROM projects
        WHERE id = ?
    """, (project_id,))

    project = cursor.fetchone()

    conn.close()

    return project


def get_project_fields(project_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            field_name,
            field_value,
            required,
            status
        FROM project_fields
        WHERE project_id = ?
        ORDER BY id
    """, (project_id,))

    fields = cursor.fetchall()

    conn.close()

    return fields


def set_project_status(project_id, status):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE projects
        SET status = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        status,
        datetime.now().isoformat(),
        project_id
    ))

    conn.commit()
    conn.close()
