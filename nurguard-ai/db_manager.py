import os
import sqlite3
import uuid
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
        padding: 10px;
        background-color: #D1FAE5;
        color: #065F46;
        border-radius: 5px;
        font-weight: bold;
        border-left: 5px solid #10B981;
    }
    .status-tampered {
        padding: 10px;
        background-color: #FEE2E2;
        color: #991B1B;
        border-radius: 5px;
        font-weight: bold;
        border-left: 5px solid #EF4444;
    }
    .timeline-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #F3F4F6;
        margin-bottom: 10px;
        border-left: 3px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🛡️ NurGuard AI — Digital Evidence Integrity")
st.caption("Track H: Proving Digital Evidence Has Not Been Changed | ICSC 2026 Universities Hackathon")

# Sidebar - Project Overview
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
                # Save uploaded file to disk with a unique prefix,
                # so two evidence files with the same name never collide
                unique_prefix = uuid.uuid4().hex[:8]
                safe_filename = f"{unique_prefix}_{uploaded_file.name}"
                filepath = os.path.join(UPLOAD_DIR, safe_filename)
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
        # Create a dropdown mapping for files
        file_options = {f"{filename} ({file_id})": (file_id, filename) for file_id, filename, _, _ in evidence_list}
        selected_option = st.selectbox("Select Evidence to Inspect", list(file_options.keys()))
        selected_id, selected_name = file_options[selected_option]
        filepath = os.path.join(UPLOAD_DIR, selected_name)
        
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
                    if is_secure:
                        st.success(f"Integrity Verified! File is completely untampered. Status: {status_msg}")
                    else:
                        st.error(f"ALERT: Tampering Detected! Status: {status_msg}")
                    st.rerun()
            
            # Action: Simulate Tampering
            if st.button("⚠️ Simulate Malicious Tampering", type="primary", use_container_width=True):
                if os.path.exists(filepath):
                    try:
                        # Slightly alter the content of the file
                        with open(filepath, "a") as f:
                            f.write("\n[ALTERED BY TAMPER SIMULATOR]")
                        st.warning("File has been slightly altered on disk! Re-run 'Verify Evidence Integrity' to see the security system catch it.")
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
        
        # Generate raw report
        report_text = db_manager.generate_section84_report(selected_id)
        
        st.code(report_text, language="text")
        
        st.download_button(
            label="💾 Download Admissibility Certificate (TXT)",
            data=report_text,
            file_name=f"section84_certificate_{selected_id}.txt",
            mime="text/plain",
            use_container_width=True
        )import os
import sqlite3
import uuid
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
        padding: 10px;
        background-color: #D1FAE5;
        color: #065F46;
        border-radius: 5px;
        font-weight: bold;
        border-left: 5px solid #10B981;
    }
    .status-tampered {
        padding: 10px;
        background-color: #FEE2E2;
        color: #991B1B;
        border-radius: 5px;
        font-weight: bold;
        border-left: 5px solid #EF4444;
    }
    .timeline-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #F3F4F6;
        margin-bottom: 10px;
        border-left: 3px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🛡️ NurGuard AI — Digital Evidence Integrity")
st.caption("Track H: Proving Digital Evidence Has Not Been Changed | ICSC 2026 Universities Hackathon")

# Sidebar - Project Overview
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
                # Save uploaded file to disk with a unique prefix,
                # so two evidence files with the same name never collide
                unique_prefix = uuid.uuid4().hex[:8]
                safe_filename = f"{unique_prefix}_{uploaded_file.name}"
                filepath = os.path.join(UPLOAD_DIR, safe_filename)
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
        # Create a dropdown mapping for files
        file_options = {f"{filename} ({file_id})": (file_id, filename) for file_id, filename, _, _ in evidence_list}
        selected_option = st.selectbox("Select Evidence to Inspect", list(file_options.keys()))
        selected_id, selected_name = file_options[selected_option]
        filepath = os.path.join(UPLOAD_DIR, selected_name)
        
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
                    if is_secure:
                        st.success(f"Integrity Verified! File is completely untampered. Status: {status_msg}")
                    else:
                        st.error(f"ALERT: Tampering Detected! Status: {status_msg}")
                    st.rerun()
            
            # Action: Simulate Tampering
            if st.button("⚠️ Simulate Malicious Tampering", type="primary", use_container_width=True):
                if os.path.exists(filepath):
                    try:
                        # Slightly alter the content of the file
                        with open(filepath, "a") as f:
                            f.write("\n[ALTERED BY TAMPER SIMULATOR]")
                        st.warning("File has been slightly altered on disk! Re-run 'Verify Evidence Integrity' to see the security system catch it.")
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
        
        # Generate raw report
        report_text = db_manager.generate_section84_report(selected_id)
        
        st.code(report_text, language="text")
        
        st.download_button(
            label="💾 Download Admissibility Certificate (TXT)",
            data=report_text,
            file_name=f"section84_certificate_{selected_id}.txt",
            mime="text/plain",
            use_container_width=True
        )import os
import sqlite3
import uuid
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
        padding: 10px;
        background-color: #D1FAE5;
        color: #065F46;
        border-radius: 5px;
        font-weight: bold;
        border-left: 5px solid #10B981;
    }
    .status-tampered {
        padding: 10px;
        background-color: #FEE2E2;
        color: #991B1B;
        border-radius: 5px;
        font-weight: bold;
        border-left: 5px solid #EF4444;
    }
    .timeline-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #F3F4F6;
        margin-bottom: 10px;
        border-left: 3px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("🛡️ NurGuard AI — Digital Evidence Integrity")
st.caption("Track H: Proving Digital Evidence Has Not Been Changed | ICSC 2026 Universities Hackathon")

# Sidebar - Project Overview
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
                # Save uploaded file to disk with a unique prefix,
                # so two evidence files with the same name never collide
                unique_prefix = uuid.uuid4().hex[:8]
                safe_filename = f"{unique_prefix}_{uploaded_file.name}"
                filepath = os.path.join(UPLOAD_DIR, safe_filename)
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
        # Create a dropdown mapping for files
        file_options = {f"{filename} ({file_id})": (file_id, filename) for file_id, filename, _, _ in evidence_list}
        selected_option = st.selectbox("Select Evidence to Inspect", list(file_options.keys()))
        selected_id, selected_name = file_options[selected_option]
        filepath = os.path.join(UPLOAD_DIR, selected_name)
        
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
                    if is_secure:
                        st.success(f"Integrity Verified! File is completely untampered. Status: {status_msg}")
                    else:
                        st.error(f"ALERT: Tampering Detected! Status: {status_msg}")
                    st.rerun()
            
            # Action: Simulate Tampering
            if st.button("⚠️ Simulate Malicious Tampering", type="primary", use_container_width=True):
                if os.path.exists(filepath):
                    try:
                        # Slightly alter the content of the file
                        with open(filepath, "a") as f:
                            f.write("\n[ALTERED BY TAMPER SIMULATOR]")
                        st.warning("File has been slightly altered on disk! Re-run 'Verify Evidence Integrity' to see the security system catch it.")
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
        
        # Generate raw report
        report_text = db_manager.generate_section84_report(selected_id)
        
        st.code(report_text, language="text")
        
        st.download_button(
            label="💾 Download Admissibility Certificate (TXT)",
            data=report_text,
            file_name=f"section84_certificate_{selected_id}.txt",
            mime="text/plain",
            use_container_width=True
        )
