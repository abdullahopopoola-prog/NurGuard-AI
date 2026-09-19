import os
import sqlite3
import streamlit as st
from datetime import datetime
import db_manager

# Ensure local directories and databases exist
UPLOAD_DIR = "secured_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
db_manager.init_db()

# Page configuration
st.set_page_config(
    page_title="NurGuard AI - Digital Evidence Integrity Workbench",
    page_icon="🛡️",
    layout="wide"
)

# Brand colors and CSS style injection
st.markdown("""
<style>
    .report-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1E3A8A;
        font-weight: bold;
    }
    .status-secure {
        padding: 12px;
        background-color: #D1FAE5;
        color: #065F46;
        border-radius: 6px;
        font-weight: bold;
        border-left: 6px solid #10B981;
        margin-bottom: 15px;
    }
    .status-tampered {
        padding: 12px;
        background-color: #FEE2E2;
        color: #991B1B;
        border-radius: 6px;
        font-weight: bold;
        border-left: 6px solid #EF4444;
        margin-bottom: 15px;
    }
    .timeline-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #F3F4F6;
        margin-bottom: 10px;
        border-left: 4px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🛡️ NurGuard AI — Digital Evidence Integrity")
st.caption("Track H: Proving Digital Evidence Has Not Been Changed | ICSC 2026 Universities Hackathon")

# Sidebar - Project Overview & Utilities
with st.sidebar:
    st.header("Project Info")
    st.markdown("""
    **NurGuard AI** is a working prototype designed to secure digital evidence at the moment of collection. 
    It generates tamper-evident cryptographic fingerprints (SHA-256) and tracks handlers over an offline-first SQLite database.
    
    ### 🎨 Brand Identity
    * **Colors:** Deep Navy, Dark Charcoal, Emerald Green
    * **Symbol:** Geometric Shield (N & G)
    """)
    st.info("💡 **Section 84 Compliance**: This prototype automatically compiles admissibility certificates matching the standards of the **Nigerian Evidence Act 2011**.")
    
    st.markdown("---")
    st.subheader("⚙️ System Utilities")
    if st.button("🧹 Clear All Logs & Data", use_container_width=True):
        try:
            if hasattr(db_manager, "clear_all_data"):
                db_manager.clear_all_data()
            else:
                conn = sqlite3.connect(db_manager.DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custody_log")
                cursor.execute("DELETE FROM evidence")
                conn.commit()
                conn.close()
                for f in os.listdir(UPLOAD_DIR):
                    os.remove(os.path.join(UPLOAD_DIR, f))
            st.success("All evidence records and files cleared!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing data: {e}")

# Helper to get all evidence items from SQLite
def get_all_evidence():
    conn = sqlite3.connect(db_manager.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, filename, original_hash, status FROM evidence ORDER BY timestamp_collected DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Tabs for 3 UI Screens
tab1, tab2, tab3 = st.tabs([
    "📥 1. Upload & Secure Evidence", 
    "⛓️ 2. Chain of Custody & Verification", 
    "⚖️ 3. Section 84 Court Admissibility"
])

# ==========================================
# TAB 1: UPLOAD & SECURE EVIDENCE
# ==========================================
with tab1:
    st.header("Upload & Record Evidence")
    st.write("Upload a digital evidence file (CCTV log, message export, log file) and secure it with a tamper-evident hash.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        officer_name = st.text_input("Collecting Officer's Name", placeholder="e.g., Inspector Ahmed Musa")
        uploaded_file = st.file_uploader("Select Evidence File", type=["txt", "csv", "log", "png", "jpg", "pdf", "mp4"])
        
        if st.button("🔐 Secure Evidence", use_container_width=True):
            if not officer_name:
                st.error("Please enter the collecting officer's name.")
            elif not uploaded_file:
                st.error("Please upload a file to secure.")
            else:
                filepath = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(filepath, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    file_id, file_hash = db_manager.secure_evidence(filepath, officer_name)
                    st.success("Evidence Secured Successfully!")
                    st.balloons()
                    
                    st.markdown(f"""
                    * **Evidence ID:** `{file_id}`
                    * **Stored Filename:** `{uploaded_file.name}`
                    * **SHA-256 Hash:** `{file_hash}`
                    """)
                except Exception as e:
                    st.error(f"Error securing evidence: {e}")

    with col2:
        st.subheader("Currently Secured Files")
        evidence_list = get_all_evidence()
        if not evidence_list:
            st.info("No evidence files secured yet. Use the upload panel on the left to start.")
        else:
            for file_id, filename, orig_hash, status in evidence_list:
                with st.expander(f"📁 {filename} ({file_id})"):
                    st.write(f"**Original SHA-256 Hash:** `{orig_hash}`")
                    if status == "Secure":
                        st.markdown('<div class="status-secure">✓ SECURE & ADMISSIBLE</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="status-tampered">⚠️ TAMPERED / ALTERED</div>', unsafe_allow_html=True)


# ==========================================
# TAB 2: CHAIN OF CUSTODY & VERIFICATION
# ==========================================
with tab2:
    st.header("Chain of Custody Timeline")
    st.write("Track who handled the evidence, record transfers, verify file integrity, and simulate tampering to test the system.")
    
    evidence_list = get_all_evidence()
    
    if not evidence_list:
        st.info("Please secure an evidence file first in Tab 1.")
    else:
        file_options = {f"{filename} ({file_id})": (file_id, filename) for file_id, filename, _, _ in evidence_list}
        selected_option = st.selectbox("Select Evidence to Inspect", list(file_options.keys()))
        selected_id, selected_name = file_options[selected_option]
        filepath = os.path.join(UPLOAD_DIR, selected_name)
        
        # Get current DB status for the selected file
        conn = sqlite3.connect(db_manager.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT status, original_hash FROM evidence WHERE file_id = ?", (selected_id,))
        db_rec = cursor.fetchone()
        conn.close()
        
        curr_status = db_rec[0] if db_rec else "Secure"
        orig_hash = db_rec[1] if db_rec else ""
        
        # Persistent Status Indicator Banner at Top of Inspection Screen
        if curr_status == "Secure":
            st.markdown('<div class="status-secure">✓ STATUS: SECURE & ADMISSIBLE (Baseline Hash Intact)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-tampered">⚠️ STATUS: TAMPERED / ALTERED — HASH MISMATCH DETECTED!</div>', unsafe_allow_html=True)
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("Log Custody Transfer")
            handler_name = st.text_input("Recipient / Handler Name", placeholder="e.g., Analyst Chioma Obi")
            action_taken = st.selectbox("Action Taken", ["Viewed", "Transferred to Lab", "Analyzed", "Stored in Vault"])
            
            if st.button("📝 Log Transfer Action", use_container_width=True):
                if not handler_name:
                    st.error("Please specify who is receiving or handling the file.")
                elif not os.path.exists(filepath):
                    st.error(f"Associated file missing on disk: {filepath}")
                else:
                    try:
                        db_manager.log_custody_action(selected_id, handler_name, action_taken, filepath)
                        st.success(f"Successfully logged action: {action_taken}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error logging custody action: {e}")
            
            st.markdown("---")
            st.subheader("🛠️ Integrity & Tampering Controls")
            
            # Action: Verify Integrity
            if st.button("🔍 Verify Evidence Integrity", use_container_width=True):
                if not os.path.exists(filepath):
                    st.error("Associated file is missing from local disk!")
                else:
                    is_secure, status_msg = db_manager.verify_integrity(selected_id, filepath)
                    current_disk_hash = db_manager.calculate_sha256(filepath)
                    
                    if is_secure:
                        st.success(f"✓ INTEGRITY VERIFIED: File is completely untampered!")
                        st.info(f"**SHA-256 Hash:** `{current_disk_hash}`")
                    else:
                        st.error(f"⚠️ ALERT: TAMPERING DETECTED! HASH MISMATCH!")
                        st.markdown(f"""
                        <div class="status-tampered">
                            <h4>⚠️ TAMPER DETECTED / HASH MISMATCH</h4>
                            <p><b>Original Baseline Hash:</b><br><code>{orig_hash}</code></p>
                            <p><b>Current Disk File Hash:</b><br><code>{current_disk_hash}</code></p>
                            <p><i>The file content on disk does not match the original cryptographic fingerprint captured at collection. This evidence is altered and legally inadmissible.</i></p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Action: Simulate Tampering
            if st.button("⚠️ Simulate Malicious Tampering", type="primary", use_container_width=True):
                if os.path.exists(filepath):
                    try:
                        # Append bytes to file regardless of file extension
                        with open(filepath, "ab") as f:
                            f.write(b"\n[ALTERED BY TAMPER SIMULATOR]")
                        
                        # Immediately update DB status so UI reflects tampering
                        conn = sqlite3.connect(db_manager.DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE evidence SET status = ? WHERE file_id = ?", ("⚠️ TAMPERED", selected_id))
                        conn.commit()
                        conn.close()
                        
                        st.warning("⚠️ File content altered on disk! Click 'Verify Evidence Integrity' above to inspect the hash mismatch.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not simulate tampering: {e}")
                else:
                    st.error("File is missing on disk; cannot tamper.")
                    
        with col_right:
            st.subheader("Chronological Custody Trail")
            trail = db_manager.get_custody_trail(selected_id)
            
            for idx, (handler, action, dt, hash_val) in enumerate(trail, 1):
                st.markdown(f"""
                <div class="timeline-card">
                    <h4><b>[{idx}] {action}</b></h4>
                    <p style='margin: 0;'>👤 <b>By:</b> {handler} | 🕒 <b>Date:</b> {dt}</p>
                    <p style='margin: 0; font-family: monospace; font-size: 0.85em;'>🔑 <b>Hash at processing:</b> {hash_val}</p>
                </div>
                """, unsafe_allow_html=True)


# ==========================================
# TAB 3: SECTION 84 COURT ADMISSIBILITY
# ==========================================
with tab3:
    st.header("Section 84 Evidence Admissibility Certificate")
    st.write("Generate and export a print-ready legal document satisfying **Section 84 of the Nigerian Evidence Act 2011**.")
    
    evidence_list = get_all_evidence()
    
    if not evidence_list:
        st.info("Please secure an evidence file first in Tab 1.")
    else:
        file_options = {f"{filename} ({file_id})": file_id for file_id, filename, _, _ in evidence_list}
        selected_option = st.selectbox("Select Evidence for Certificate", list(file_options.keys()))
        selected_id = file_options[selected_option]
        
        report_text = db_manager.generate_section84_report(selected_id)
        
        st.code(report_text, language="text")
        
        st.download_button(
            label="💾 Download Admissibility Certificate (TXT)",
            data=report_text,
            file_name=f"section84_certificate_{selected_id}.txt",
            mime="text/plain",
            use_container_width=True
        )
