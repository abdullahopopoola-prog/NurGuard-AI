"""
test_db_manager.py
Verifies two things:
  1. Every function app.py calls still behaves exactly as before
     (same signatures, same return shapes) - nothing broke.
  2. The new hash-chain feature actually catches tampering with the
     custody_log table itself.

Run with: pytest test_db_manager.py -v
"""
import os
import sqlite3
import pytest
import db_manager


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "evidence.db")
    db_manager.init_db(path)
    return path


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "sample_evidence.txt"
    f.write_text("original evidence content")
    return str(f)


# ---- Compatibility with app.py's exact usage pattern ----

def test_secure_evidence_matches_app_py_usage(db_path, sample_file):
    file_id, file_hash = db_manager.secure_evidence(sample_file, "Officer Musa", db_path=db_path)
    assert file_id.startswith("EVID_")
    assert len(file_hash) == 64  # sha256 hex length


def test_log_custody_action_matches_app_py_usage(db_path, sample_file):
    file_id, _ = db_manager.secure_evidence(sample_file, "Officer Musa", db_path=db_path)
    # Should not raise - same call shape app.py uses
    db_manager.log_custody_action(file_id, "Analyst Bello", "Transferred", sample_file, db_path=db_path)


def test_verify_integrity_matches_app_py_usage(db_path, sample_file):
    file_id, _ = db_manager.secure_evidence(sample_file, "Officer Musa", db_path=db_path)
    is_secure, status_msg = db_manager.verify_integrity(file_id, sample_file, db_path=db_path)
    assert is_secure is True
    assert status_msg == "Secure"

    with open(sample_file, "a") as f:
        f.write("tampered")

    is_secure, status_msg = db_manager.verify_integrity(file_id, sample_file, db_path=db_path)
    assert is_secure is False
    assert "TAMPERED" in status_msg


def test_get_custody_trail_matches_app_py_usage(db_path, sample_file):
    file_id, _ = db_manager.secure_evidence(sample_file, "Officer Musa", db_path=db_path)
    db_manager.log_custody_action(file_id, "Analyst Bello", "Transferred", sample_file, db_path=db_path)

    trail = db_manager.get_custody_trail(file_id, db_path=db_path)
    assert len(trail) == 2
    # Same 4-column tuple shape as before: (handler_name, action_taken, action_timestamp, current_hash)
    assert trail[0][0] == "Officer Musa"
    assert trail[0][1] == "Collected"


def test_generate_section84_report_still_works(db_path, sample_file):
    file_id, _ = db_manager.secure_evidence(sample_file, "Officer Musa", db_path=db_path)
    report = db_manager.generate_section84_report(file_id, db_path=db_path)
    assert isinstance(report, str)
    assert "Collected" in report


# ---- New: hash-chain tamper detection ----

def test_chain_integrity_true_when_untouched(db_path, sample_file):
    file_id, _ = db_manager.secure_evidence(sample_file, "Officer Musa", db_path=db_path)
    db_manager.log_custody_action(file_id, "Analyst Bello", "Transferred", sample_file, db_path=db_path)

    assert db_manager.verify_log_chain_integrity(file_id, db_path=db_path) is True


def test_chain_integrity_false_if_log_row_edited_directly(db_path, sample_file):
    file_id, _ = db_manager.secure_evidence(sample_file, "Officer Musa", db_path=db_path)
    db_manager.log_custody_action(file_id, "Analyst Bello", "Transferred", sample_file, db_path=db_path)

    # Simulate someone bypassing the API and editing the log directly
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE custody_log SET handler_name = 'Forged Name' WHERE file_id = ? AND action_taken = 'Transferred'",
        (file_id,)
    )
    conn.commit()
    conn.close()

    assert db_manager.verify_log_chain_integrity(file_id, db_path=db_path) is False


def test_migration_adds_columns_to_pre_existing_database(tmp_path):
    """Simulates the committed evidence.db: a database created by the
    ORIGINAL db_manager.py (no chain columns), then opened by the NEW
    version. init_db() should add the columns without errors or data loss."""
    path = str(tmp_path / "legacy.db")

    # Create an old-style database with the original schema (no chain columns)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE evidence (
            file_id TEXT PRIMARY KEY, filename TEXT NOT NULL,
            original_hash TEXT NOT NULL, timestamp_collected TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE custody_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT, file_id TEXT,
            handler_name TEXT NOT NULL, action_taken TEXT NOT NULL,
            action_timestamp TEXT NOT NULL, current_hash TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES evidence (file_id)
        )
    """)
    conn.execute(
        "INSERT INTO evidence VALUES ('EVID_OLD', 'old.txt', 'abc123', '2026-01-01T00:00:00', 'Secure')"
    )
    conn.execute(
        "INSERT INTO custody_log (file_id, handler_name, action_taken, action_timestamp, current_hash) "
        "VALUES ('EVID_OLD', 'Officer X', 'Collected', '2026-01-01T00:00:00', 'abc123')"
    )
    conn.commit()
    conn.close()

    # Now run the NEW init_db() against this legacy file
    db_manager.init_db(path)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(custody_log)")
    columns = {row[1] for row in cursor.fetchall()}
    # Old data still there
    cursor.execute("SELECT COUNT(*) FROM custody_log")
    count = cursor.fetchone()[0]
    conn.close()

    assert "prev_log_hash" in columns
    assert "entry_hash" in columns
    assert count == 1  # old row preserved, not wiped
