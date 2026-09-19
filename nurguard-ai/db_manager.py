import os
import sqlite3
import hashlib
from datetime import datetime

# Database Name
DB_NAME = "evidence.db"

def init_db(db_path=DB_NAME):
    """
    Initializes the local SQLite database and creates the necessary tables
    for evidence metadata and chain of custody tracking.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Evidence table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        file_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        original_hash TEXT NOT NULL,
        timestamp_collected TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

    # Create Custody Log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custody_log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id TEXT,
        handler_name TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        action_timestamp TEXT NOT NULL,
        current_hash TEXT NOT NULL,
        FOREIGN KEY (file_id) REFERENCES evidence (file_id)
    )
    """)

    conn.commit()

    # --- ADDITION (not in original): make sure hash-chain columns exist ---
    # Safe on both a brand-new database and the evidence.db already
    # committed to the repo. Never touches existing rows.
    _ensure_chain_columns(conn)
    conn.commit()
    conn.close()


# ================================================================
# ADDITION (not in original): hash-chain support for tamper-evident
# custody logs. Nothing below this block changes any existing
# function's name, parameters, or return value.
# ================================================================
def _ensure_chain_columns(conn):
    """
    Adds prev_log_hash and entry_hash columns to custody_log if they don't
    already exist. Lets the chain feature work on databases created before
    this change, without losing any existing rows.

    NOTE: rows created BEFORE this migration have NULL entry_hash, since
    they predate the chain feature. verify_log_chain_integrity() treats
    those as unchained "legacy" rows rather than flagging them as
    tampered - the chain applies going forward from here. If evidence.db
    only has test/dummy data in it, the cleanest option is to delete it
    once and let it regenerate fresh, so every entry is chain-protected
    from the start.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(custody_log)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "prev_log_hash" not in existing_columns:
        cursor.execute("ALTER TABLE custody_log ADD COLUMN prev_log_hash TEXT")
    if "entry_hash" not in existing_columns:
        cursor.execute("ALTER TABLE custody_log ADD COLUMN entry_hash TEXT")


def _last_log_entry_hash(cursor, file_id):
    """Internal: entry_hash of the most recent chained log row for this
    file_id, or 'GENESIS' if there isn't a chained entry yet."""
    cursor.execute(
        "SELECT entry_hash FROM custody_log WHERE file_id = ? ORDER BY log_id DESC LIMIT 1",
        (file_id,)
    )
    row = cursor.fetchone()
    return row[0] if (row and row[0]) else "GENESIS"


def _compute_entry_hash(file_id, handler_name, action_taken, action_timestamp, current_hash, prev_hash):
    payload = f"{file_id}|{handler_name}|{action_taken}|{action_timestamp}|{current_hash}|{prev_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_log_chain_integrity(file_id, db_path=DB_NAME):
    """
    NEW FUNCTION - does not replace or change anything existing.

    Confirms the custody_log itself has not been edited or deleted after
    the fact, by recomputing the hash chain and comparing it to what's
    stored. Catches tampering with the LOG (e.g. someone editing a row
    directly with SQL), which verify_integrity() cannot see, since that
    function only checks the evidence FILE on disk.

    Returns True if every chained entry checks out. Legacy rows without
    an entry_hash (created before this feature existed) are skipped -
    see the note in _ensure_chain_columns().
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT file_id, handler_name, action_taken, action_timestamp,
               current_hash, prev_log_hash, entry_hash
        FROM custody_log WHERE file_id = ? ORDER BY log_id ASC
    """, (file_id,))
    rows = cursor.fetchall()
    conn.close()

    expected_prev = "GENESIS"
    for (fid, handler, action, ts, cur_hash, prev_hash, entry_hash) in rows:
        if entry_hash is None:
            continue  # legacy row, predates the chain feature
        if prev_hash != expected_prev:
            return False
        recomputed = _compute_entry_hash(fid, handler, action, ts, cur_hash, prev_hash)
        if recomputed != entry_hash:
            return False
        expected_prev = entry_hash
    return True
# ================================================================
# END ADDITION
# ================================================================


def calculate_sha256(filepath):
    """
    Generates a deterministic SHA-256 cryptographic hash of a file's binary content
    to act as its unique digital fingerprint.
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in chunks to prevent memory errors with large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def secure_evidence(filepath, officer_name, db_path=DB_NAME):
    """
    Records new evidence: computes its SHA-256 hash, inserts a record into
    the evidence table as 'Secure', and logs the initial 'Collected' action.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    filename = os.path.basename(filepath)
    import uuid  # add this to the imports at the top of db_manager.py

    file_id = f"EVID_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
    file_hash = calculate_sha256(filepath)
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    _ensure_chain_columns(conn)  # ADDITION: safety net if init_db() wasn't called first

    try:
        # Insert evidence metadata
        cursor.execute("""
        INSERT INTO evidence (file_id, filename, original_hash, timestamp_collected, status)
        VALUES (?, ?, ?, ?, ?)
        """, (file_id, filename, file_hash, timestamp, "Secure"))

        # ADDITION: compute chain hash for this log entry
        prev_hash = _last_log_entry_hash(cursor, file_id)
        entry_hash = _compute_entry_hash(file_id, officer_name, "Collected", timestamp, file_hash, prev_hash)

        # Log initial custody trail entry
        cursor.execute("""
        INSERT INTO custody_log (file_id, handler_name, action_taken, action_timestamp, current_hash, prev_log_hash, entry_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_id, officer_name, "Collected", timestamp, file_hash, prev_hash, entry_hash))

        conn.commit()
        return file_id, file_hash
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def log_custody_action(file_id, handler_name, action_taken, filepath, db_path=DB_NAME):
    """
    Logs an action taken on the evidence (e.g., 'Viewed', 'Transferred')
    and recalculates the hash to guarantee integrity at the moment of handling.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Associated file not found: {filepath}")

    current_hash = calculate_sha256(filepath)
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    _ensure_chain_columns(conn)  # ADDITION: safety net

    try:
        # Check if evidence exists
        cursor.execute("SELECT file_id FROM evidence WHERE file_id = ?", (file_id,))
        if not cursor.fetchone():
            raise ValueError(f"Evidence ID {file_id} not found in database.")

        # ADDITION: compute chain hash for this log entry
        prev_hash = _last_log_entry_hash(cursor, file_id)
        entry_hash = _compute_entry_hash(file_id, handler_name, action_taken, timestamp, current_hash, prev_hash)

        cursor.execute("""
        INSERT INTO custody_log (file_id, handler_name, action_taken, action_timestamp, current_hash, prev_log_hash, entry_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_id, handler_name, action_taken, timestamp, current_hash, prev_hash, entry_hash))

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_custody_trail(file_id, db_path=DB_NAME):
    """
    Retrieves the chronological audit trail of all custody actions for a file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT handler_name, action_taken, action_timestamp, current_hash
    FROM custody_log
    WHERE file_id = ?
    ORDER BY log_id ASC
    """, (file_id,))
    logs = cursor.fetchall()
    conn.close()
    return logs

def verify_integrity(file_id, filepath, db_path=DB_NAME):
    """
    Verifies if the file's current hash matches the database original_hash.
    Updates the evidence status to 'TAMPERED' if a mismatch is found.
    """
    if not os.path.exists(filepath):
        return False, "File missing on disk"

    current_hash = calculate_sha256(filepath)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT original_hash FROM evidence WHERE file_id = ?", (file_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return False, "Evidence record not found in database"

    original_hash = result[0]

    if current_hash == original_hash:
        status_msg = "Secure"
        is_secure = True
    else:
        status_msg = "\u26a0\ufe0f TAMPERED"
        is_secure = False

        # Update status in evidence table
        cursor.execute("UPDATE evidence SET status = ? WHERE file_id = ?", (status_msg, file_id))
        conn.commit()

    conn.close()
    return is_secure, status_msg

def generate_section84_report(file_id, db_path=DB_NAME):
    """
    Generates an automated compliance report matching the legal requirements
    of Section 84 of the Nigerian Evidence Act 2011.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT filename, original_hash, timestamp_collected, status FROM evidence WHERE file_id = ?", (file_id,))
    evidence = cursor.fetchone()

    if not evidence:
        conn.close()
        return "Evidence record not found."

    filename, original_hash, timestamp_collected, status = evidence
    trail = get_custody_trail(file_id, db_path)

    conn.close()

    report = []
    report.append("================================================================")
    report.append("          SECTION 84 EVIDENCE ADMISSIBILITY CERTIFICATE         ")
    report.append("               Pursuant to Nigerian Evidence Act 2011           ")
    report.append("================================================================")
    report.append(f"Evidence ID:        {file_id}")
    report.append(f"File Name:          {filename}")
    report.append(f"Original SHA-256:   {original_hash}")
    report.append(f"Recorded Date/Time: {timestamp_collected}")
    report.append(f"Current Status:     {status}")
    report.append("----------------------------------------------------------------")
    report.append("CHRONOLOGICAL CHAIN OF CUSTODY LOGS:")
    for idx, (handler, action, dt, h_val) in enumerate(trail, 1):
        report.append(f"  [{idx}] Action: {action} | By: {handler} | Date: {dt}")
        report.append(f"      Cryptographic Fingerprint: {h_val}")
    report.append("----------------------------------------------------------------")
    report.append("STATUTORY COMPLIANCE DECLARATION (SECTION 84):")
    report.append("I, the undersigned responsible officer, do hereby certify that:")
    report.append("1. The digital device producing this record was operating properly.")
    report.append("2. The source document was supplied in the ordinary course of business.")
    report.append("3. The data integrity of the file is cryptographically verified.")
    report.append("4. No unauthorized alteration has occurred since ingestion.")
    report.append("")
    report.append("Officer Signature: _______________________")
    report.append("Date: _________________________________")
    report.append("================================================================")

    return "\n".join(report)
