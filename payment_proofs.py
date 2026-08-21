import sqlite3


def save_payment_proof(
    subscription_id,
    user_id,
    transaction_reference=None,
    receipt_file_id=None,
    receipt_type=None
):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO payment_proofs
        (
            subscription_id,
            user_id,
            transaction_reference,
            receipt_file_id,
            receipt_type,
            status
        )
        VALUES (?, ?, ?, ?, ?, 'PENDING')
        """,
        (
            subscription_id,
            user_id,
            transaction_reference,
            receipt_file_id,
            receipt_type
        )
    )

    proof_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return proof_id


def get_pending_proofs():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            subscription_id,
            user_id,
            transaction_reference,
            receipt_file_id,
            receipt_type,
            status,
            submitted_at
        FROM payment_proofs
        WHERE status = 'PENDING'
        ORDER BY id DESC
        """
    )

    results = cursor.fetchall()

    conn.close()

    return results


def mark_proof_verified(proof_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE payment_proofs
        SET status = 'VERIFIED'
        WHERE id = ?
        """,
        (proof_id,)
    )

    conn.commit()
    conn.close()


def mark_proof_rejected(proof_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE payment_proofs
        SET status = 'REJECTED'
        WHERE id = ?
        """,
        (proof_id,)
    )

    conn.commit()
    conn.close()
