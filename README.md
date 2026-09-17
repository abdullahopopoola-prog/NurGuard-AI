# NurGuard AI

**ICSC 2026 Universities Hackathon — Track H**  
**Proving Digital Evidence Has Not Been Changed**

NurGuard AI is a simple, offline-capable prototype that helps verify whether a digital file has changed after it was collected.

It creates a **SHA-256 fingerprint** for a file, records basic custody information, detects later modifications, and generates a short integrity report.

> **Team:** NurGuard AI — An-Nahda Labs

---

## 🔗 Links

- **Live Demo:** https://nurguard-ai-nldwrksydlaqpq5dxxpqzp.streamlit.app/
- **GitHub Repository:** https://github.com/abdullahopopoola-prog/NurGuard-AI

---

## 🧩 The Problem

Digital evidence such as documents, images, CCTV footage, chat exports, and system logs is increasingly used in investigations and legal proceedings.

One important challenge is determining whether a digital file presented later is the same file that was originally collected, or whether its contents have been changed.

In Nigeria, **Section 84 of the Evidence Act** provides requirements relating to the admissibility of electronic evidence. The Supreme Court case **Kubor v. Dickson (2013)** also highlighted the importance of properly establishing the authenticity and foundation of electronic evidence.

NurGuard AI explores a simple way to support this process by recording a file's cryptographic fingerprint and maintaining a basic custody trail.

---

## 💡 What NurGuard AI Does

NurGuard AI allows a user to:

- Upload and register a digital file
- Generate a **SHA-256 hash** (digital fingerprint)
- Record basic custody information
- Store evidence records locally using SQLite
- Check a file again at a later time
- Detect changes by comparing SHA-256 hashes
- Generate a short integrity report

The prototype is **offline-capable**, with its core records stored locally.

---

## ⚙️ How It Works

```text
Collect File
     ↓
Upload to NurGuard AI
     ↓
Generate SHA-256 Hash
     ↓
Record Custody Information
     ↓
Store Evidence Record
     ↓
Check File Later
     ↓
Generate New Hash
     ↓
Compare Hashes
     ↓
Integrity Status / Report
```

### Step-by-step

1. The user enters basic information about the evidence and uploads a file.
2. NurGuard AI calculates the file's SHA-256 hash.
3. The hash is stored together with the available custody information.
4. The file can be checked again later.
5. NurGuard AI calculates a new SHA-256 hash.
6. The new hash is compared with the original hash.
7. If the hashes match, the file contents match the original recorded fingerprint.
8. If the hashes differ, the system flags the file as changed.
9. The user can generate a short integrity report.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application logic |
| **Streamlit** | User interface |
| **SQLite** | Local database and custody records |
| **SHA-256** | Cryptographic file fingerprinting |

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/abdullahopopoola-prog/NurGuard-AI.git
cd NurGuard-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser using the local Streamlit address shown in the terminal.

---

## 📁 Project Structure

```text
NurGuard-AI/
│
├── app.py              # Streamlit interface
├── db_manager.py       # Hashing and database logic
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 👥 Team

**NurGuard AI — An-Nahda Labs**

| Role | Responsibility |
|---|---|
| Technical Lead | Project coordination and architecture |
| Backend Developer | Hashing and database |
| Frontend Developer | Streamlit interface |
| Researcher | Legal context and Nigerian cases |
| Designer | Logo and project branding |
| Tester | Testing and bug reporting |
| Video / Demo | Demonstration video |
| Documentation | Technical write-up |

---

## ⚠️ Limitations

NurGuard AI is a **student hackathon prototype** and is not intended to replace professional digital-forensics tools or established forensic procedures.

Current limitations include:

- Best suited for individual digital files rather than very large forensic images.
- File upload works best on **desktop browsers**; mobile support is limited.
- Custody records depend on the accuracy of information entered by the user.
- The prototype has not yet been tested in a real institutional forensic environment.
- The system does not replace professional evidence acquisition, preservation, or forensic analysis.
- A matching hash verifies that the file contents match the recorded fingerprint; it does not by itself establish the complete legal admissibility of the evidence.

---

## 🔐 Data & Privacy

For development, testing, and demonstration:

- Only **synthetic or anonymised data** is used.
- No real personal or sensitive evidence is required.
- The project does not depend on real-world case files.
- Sample files are used to demonstrate the integrity-checking workflow.

---

## 🔒 Tamper-Evident Verification

NurGuard AI provides **tamper-evident and cryptographically verifiable file-integrity checking**.

It can detect changes to a file by comparing its current SHA-256 hash with the hash recorded when the file was originally registered.

However, this does **not** mean the evidence is absolutely immutable.

The integrity of the overall process also depends on factors such as how the original file was collected, how custody information was recorded, and how the stored records are protected.

---

## 🎯 Hackathon Context

**Hackathon:** ICSC 2026 Universities Hackathon  
**Track:** H — Proving Digital Evidence Has Not Been Changed  
**Team:** NurGuard AI — An-Nahda Labs

The project explores how cryptographic hashing, basic custody records, and offline-capable technology can be combined to make digital evidence integrity easier to check and understand.

---

## 📌 Project Status

**Status: Hackathon Prototype**

NurGuard AI is an early-stage prototype. Possible future improvements include:

- Stronger audit trails
- Improved evidence metadata
- Role-based access
- More detailed integrity reports
- Additional verification methods
- Better mobile support
- Integration with formal digital-forensics workflows

---

## 📄 License

This project was developed as part of the **ICSC 2026 Universities Hackathon**.

See the repository for the applicable licensing and usage terms.
