from datetime import datetime, timedelta
import sqlite3


PLANS = {
    "week": {
        "name": "1 Week",
        "amount": 20.00,
        "days": 7
    },
    "month": {
        "name": "1 Month",
        "amount": 60.00,
        "days": 30
    },
    "three_months": {
        "name": "3 Months",
        "amount": 150.00,
        "days": 90
    }
}


def create_pending_subscription(
    user_id,
    plan_key,
    currency="USD",
    payment_method=None
):
    if plan_key not in PLANS:
        return None

    plan = PLANS[plan_key]

    started = datetime.now()
    expires = started + timedelta(days=plan["days"])

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO subscriptions
        (
            user_id,
            plan,
            amount,
            currency,
            started_at,
            expires_at,
            status,
            payment_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            plan_key,
            plan["amount"],
            currency,
            started.isoformat(),
            expires.isoformat(),
            "PENDING",
            payment_method
        )
    )

    subscription_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return subscription_id


def activate_subscription(subscription_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE subscriptions
        SET status = 'ACTIVE'
        WHERE id = ?
        """,
        (subscription_id,)
    )

    conn.commit()
    conn.close()


def get_active_subscription(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    cursor.execute(
        """
        SELECT
            id,
            plan,
            amount,
            currency,
            started_at,
            expires_at,
            status
        FROM subscriptions
        WHERE user_id = ?
        AND status = 'ACTIVE'
        AND expires_at > ?
        ORDER BY expires_at DESC
        LIMIT 1
        """,
        (user_id, now)
    )

    subscription = cursor.fetchone()

    conn.close()

    return subscription


def expire_old_subscriptions():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    cursor.execute(
        """
        UPDATE subscriptions
        SET status = 'EXPIRED'
        WHERE status = 'ACTIVE'
        AND expires_at <= ?
        """,
        (now,)
    )

    conn.commit()
    conn.close()


def set_payment_method(subscription_id, payment_method):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE subscriptions
        SET payment_method = ?
        WHERE id = ?
        """,
        (payment_method, subscription_id)
    )

    conn.commit()
    conn.close()


def get_pending_subscriptions():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            plan,
            amount,
            currency,
            payment_method,
            status,
            started_at,
            expires_at
        FROM subscriptions
        WHERE status = 'PENDING'
        ORDER BY id DESC
        """
    )

    results = cursor.fetchall()

    conn.close()

    return results


def reject_subscription(subscription_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE subscriptions
        SET status = 'REJECTED'
        WHERE id = ? AND status = 'PENDING'
        """,
        (subscription_id,)
    )

    conn.commit()
    conn.close()


def get_subscription(subscription_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            user_id,
            plan,
            amount,
            currency,
            payment_method,
            status,
            expires_at
        FROM subscriptions
        WHERE id = ?
        """,
        (subscription_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result
