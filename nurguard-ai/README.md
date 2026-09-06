# NurGuard AI

**ICSC 2026 Universities Hackathon — Track H: Proving Digital Evidence Has Not Been Changed**

NurGuard AI is an offline-first, cryptographically secured digital forensics prototype designed for Nigerian law enforcement and incident response teams. It automates the collection, chain-of-custody tracking, and verification of digital evidence, producing court-admissible authentication reports that strictly comply with **Section 84 of the Nigerian Evidence Act 2011**.

---

## ⚖️ The Problem & Legal Context

In modern Nigerian litigation, cybercrime cases, fraud investigations, and disciplinary hearings increasingly depend on digital evidence such as server logs, CCTV footage, and document exports [74]. However, this evidence is highly "malleable and mutable" [91], often copied onto insecure flash drives or shared via email with no audit trail [75]. Consequently, crucial cases are frequently lost on integrity grounds [75].

Under **Section 84 of the Nigerian Evidence Act 2011**, computer-generated evidence is only admissible if a **Certificate of Authentication** is produced [90, 108]. This certificate must prove:
1. The computer or device was operating properly at the material time [108].
2. The information was supplied in the ordinary course of business [108].
3. No unauthorized alterations occurred while the record was in custody [108].

*Kubor v. Dickson (2013)* established that compliance with these conditions is mandatory [110]. **NurGuard AI** solves this challenge by mathematically proving that evidence has not been tampered with since the exact moment of collection.

---

## 🛠️ System Architecture & Features

The system is built as an offline-first desktop prototype using **Python 3.9+**, **SQLite**, and **Streamlit** [92, 93, 100].

### 1. Cryptographic Ingestion & Hashing
* Uses Python's built-in `hashlib.sha256()` to compute a deterministic, immutable digital fingerprint of files upon upload [92, 99].
* Processes files in streamable chunks to maintain an $O(c)$ bounded memory footprint, allowing standard laptops to process massive evidence files [125, 162].

### 2. Local SQLite Chain of Custody
* Stores metadata locally in `evidence.db` to handle unstable network connections in field deployments [93, 99].
* **`evidence` Table:** Logs `file_id`, `filename`, `original_hash`, `timestamp_collected`, and current `status` [99].
* **`custody_log` Table:** Logs every interaction (Viewed, Transferred, Analyzed) detailing the officer's name, action, timestamp, and a live hash verification [99].

### 3. Streamlit Management Dashboard
* **Secure Ingestion:** Allows field officers to securely upload files, calculate initial hashes, and log custody metadata [100].
* **Chain of Custody Timeline:** Displays a vertical, chronological timeline of every user who accessed the evidence [100].
* **Tamper Verification:** Allows examiners to re-verify files. If a single character is altered, the system flags the file as **⚠️ TAMPERED / ALTERED** [99, 100].
* **Automated Section 84 Compliance Report:** Generates and exports a print-ready, legally compliant certificate containing all required statutory declarations and SHA-256 audit trails [98].

---

## 🚀 Getting Started (Local Setup)

To run this prototype on your local developer workstation using **VS Code**:

### Prerequisites
* Ensure you have **Python 3.9+** installed on your machine.

### Installation
1. Clone this repository (or download the source files):
   ```bash
   git clone https://github.com/your-username/nurguard-ai.git
   cd nurguard-ai
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
Launch the Streamlit web server:
```bash
python -m streamlit run app.py
```
A browser tab will automatically open at `http://localhost:8501`.

---

## 📦 Repository Structure
```text
nurguard-ai/
├── app.py               # Streamlit Frontend UI
├── db_manager.py        # Cryptographic Engine & SQLite Controller
├── README.md            # Project Overview & Setup Instructions
└── requirements.txt     # Python Dependencies
```

---

## 👥 Team Roles (Team NurGuard AI)

* **Technical Lead:** Orchestrates system architecture, technology selection, and code reviews [81, 82].
* **Backend Developer:** Constructs cryptographic hashing logic and the SQLite chain of custody engine [82].
* **Frontend Developer:** Designs the Streamlit user interface screens and status dashboards [82, 83].
* **Logo & Branding Designer:** Establishes the visual identity using deep navy, dark charcoal, and emerald green [83, 101].
* **Researcher:** Contextualizes legal admissibility standards and gathers real-world case studies [84, 98].
* **Tester:** Executes system vulnerability testing, offline sync validation, and file tampering simulations [84, 85].
* **Video Editor / Demo Person:** Produces the standard 3-minute walking pitch and system demonstration [83, 97].
* **PDF / Documentation Person:** Coordinates the official 4-page technical design submission [84].
