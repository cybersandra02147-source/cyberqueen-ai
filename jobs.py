import sqlite3


DB = "users.db"


def create_job(
    user_id,
    subscription_id,
    service,
    description,
    project_id=None
):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO jobs
        (
            user_id,
            subscription_id,
            service,
            description,
            status,
            project_id
        )
        VALUES (?, ?, ?, ?, 'PENDING', ?)
        """,
        (
            user_id,
            subscription_id,
            service,
            description,
            project_id
        )
    )

    job_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return job_id


def get_pending_jobs():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, user_id, subscription_id,
               service, description, status, created_at
        FROM jobs
        WHERE status IN ('PENDING', 'IN PROGRESS')
        ORDER BY id DESC
        """
    )

    jobs = cursor.fetchall()
    conn.close()

    return jobs


def get_job(job_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            subscription_id,
            service,
            description,
            status,
            created_at,
            project_id
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    )

    job = cursor.fetchone()
    conn.close()

    return job


def update_job_status(job_id, status):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE jobs
        SET status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (status, job_id)
    )

    conn.commit()
    conn.close()


def get_all_jobs():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, user_id, subscription_id,
               service, description, status, created_at
        FROM jobs
        ORDER BY id DESC
        """
    )

    jobs = cursor.fetchall()
    conn.close()

    return jobs


def set_generated_folder(job_id, folder):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE jobs
        SET generated_folder = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (folder, job_id)
    )

    conn.commit()
    conn.close()

def get_generated_folder(job_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT generated_folder
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return row[0]
