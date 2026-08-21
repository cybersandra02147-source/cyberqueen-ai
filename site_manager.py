import sqlite3
import secrets
import string
from datetime import datetime

DB = "users.db"


def generate_site_key(length=12):
    characters = string.ascii_lowercase + string.digits
    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


def create_site(
    user_id,
    job_id,
    subscription_id,
    folder,
    expires_at
):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    while True:
        site_key = generate_site_key()

        cursor.execute(
            "SELECT id FROM sites WHERE site_key = ?",
            (site_key,)
        )

        if cursor.fetchone() is None:
            break

    cursor.execute(
        """
        INSERT INTO sites
        (
            site_key,
            user_id,
            job_id,
            subscription_id,
            folder,
            expires_at,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        """,
        (
            site_key,
            user_id,
            job_id,
            subscription_id,
            folder,
            expires_at
        )
    )

    site_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return site_id, site_key


def get_site(site_key):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            site_key,
            user_id,
            job_id,
            subscription_id,
            folder,
            expires_at,
            status
        FROM sites
        WHERE site_key = ?
        """,
        (site_key,)
    )

    site = cursor.fetchone()

    conn.close()

    return site


def is_site_active(site_key):
    site = get_site(site_key)

    if not site:
        return False

    expires_at = datetime.fromisoformat(
        site[6]
    )

    now = datetime.now()

    if expires_at <= now:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE sites
            SET status = 'EXPIRED'
            WHERE site_key = ?
            """,
            (site_key,)
        )

        conn.commit()
        conn.close()

        return False

    return site[7] == "ACTIVE"
