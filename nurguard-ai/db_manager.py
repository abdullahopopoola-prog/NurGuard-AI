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
    conn.close()

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
    file_id = f"EVID_{int(datetime.now().timestamp())}"
    file_hash = calculate_sha256(filepath)
    timestamp = datetime.now().isoformat()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Insert evidence metadata
        cursor.execute("""
        INSERT INTO evidence (file_id, filename, original_hash, timestamp_collected, status)
        VALUES (?, ?, ?, ?, ?)
        """, (file_id, filename, file_hash, timestamp, "Secure"))
        
        # Log initial custody trail entry
        cursor.execute("""
        INSERT INTO custody_log (file_id, handler_name, action_taken, action_timestamp, current_hash)
        VALUES (?, ?, ?, ?, ?)
        """, (file_id, officer_name, "Collected", timestamp, file_hash))
        
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
    
    try:
        # Check if evidence exists
        cursor.execute("SELECT file_id FROM evidence WHERE file_id = ?", (file_id,))
        if not cursor.fetchone():
            raise ValueError(f"Evidence ID {file_id} not found in database.")
            
        cursor.execute("""
        INSERT INTO custody_log (file_id, handler_name, action_taken, action_timestamp, current_hash)
        VALUES (?, ?, ?, ?, ?)
        """, (file_id, handler_name, action_taken, timestamp, current_hash))
        
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
    Updates the evidence status to '⚠️ TAMPERED' if a mismatch is found.
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
        status_msg = "⚠️ TAMPERED"
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
