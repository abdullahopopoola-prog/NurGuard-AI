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
    
    col1, col2 = st.columns([1])
    
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
