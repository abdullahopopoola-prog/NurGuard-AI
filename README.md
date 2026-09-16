# NurGuard AI

**ICSC 2026 Universities Hackathon — Track H: Proving Digital Evidence Has Not Been Changed**

NurGuard AI is a simple, offline-capable prototype that helps verify whether a digital file has remained unchanged after it was collected.

The system creates a SHA-256 fingerprint for a file, records basic custody information, detects later modifications, and generates a short integrity report.

> **Team:** NurGuard AI — An-Nahda Labs

## 🔗 Links

- **GitHub Repository:** https://github.com/abdullahopopoola-prog/NurGuard-AI
- **Live Demo:** https://nurguard-ai-9dhapp7nueelbcdk68d8skj.streamlit.app/

## 🧩 The Problem

Digital evidence such as CCTV footage, documents, images, chat exports, and system logs is increasingly used in investigations and legal proceedings.

A key challenge is proving that a digital file presented later is the same file that was originally collected and that it has not been altered along the way.

In Nigeria, **Section 84 of the Evidence Act** provides requirements for the admissibility of electronic evidence. The Supreme Court decision in **Kubor v. Dickson (2013)** also highlighted the importance of properly establishing the authenticity and origin of electronic evidence.

NurGuard AI explores a simple way to support this process by creating a verifiable digital fingerprint and maintaining a basic custody record from the point of collection.

## 💡 What NurGuard AI Does

NurGuard AI allows a user to:

- Upload and register a digital file
- Generate a **SHA-256 hash** for the file
- Record basic custody information
- Store the evidence record locally
- Re-check a file at a later time
- Detect changes by comparing SHA-256 hashes
- Generate a simple integrity report

The prototype is designed to work **offline**, making it suitable for environments where reliable internet access may not always be available.

## ⚙️ How It Works

The basic workflow is:

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
Re-check File Later
     ↓
Compare Hashes
     ↓
Integrity Status / Report
```

### Step-by-step

1. The user provides basic information about the evidence and uploads a file.
2. NurGuard AI calculates the file's SHA-256 hash.
3. The hash is stored together with the available custody information.
4. The file can later be checked again.
5. NurGuard AI calculates a new SHA-256 hash.
6. The new hash is compared with the original hash.
7. If the hashes match, the file has not changed since the original record.
8. If the hashes differ, the system flags the file as changed.
9. An integrity report can then be generated.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application logic |
| **Streamlit** | Web interface |
| **SQLite** | Local evidence and custody records |
| **SHA-256** | Digital file fingerprinting |

The prototype uses free and widely available technologies.

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/abdullahopopoola-prog/NurGuard-AI.git
cd NurGuard-AI
```

### 2. Install the dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
python -m streamlit run app.py
```

The application should then open in the browser at the local Streamlit address provided in the terminal.

## 📁 Project Structure

```text
NurGuard-AI/
│
├── app.py              # Streamlit application
├── db_manager.py       # Hashing and database logic
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 👥 Team

**NurGuard AI — An-Nahda Labs**

The project was developed as a collaborative student hackathon project.

| Role | Responsibility |
|---|---|
| Technical Lead | Project coordination and system architecture |
| Backend Developer | Hashing and database functionality |
| Frontend Developer | Streamlit interface |
| Researcher | Legal context and supporting research |
| Tester | Testing and bug reporting |
| Design & Branding | Visual identity and project materials |
| Video & Demo | Demonstration video and presentation |
| Documentation | Technical documentation |

## ⚠️ Limitations

NurGuard AI is a **student hackathon prototype**, not a replacement for professional digital-forensics software.

Current limitations include:

- Best suited for individual digital files rather than very large forensic disk images.
- The custody record depends on the accuracy of information entered by the user.
- The prototype has not been tested in a real institutional forensic environment.
- It does not replace established forensic acquisition, preservation, or investigation procedures.
- A matching hash shows that the file contents match the recorded file; it does not by itself establish the complete legal admissibility of the evidence.

## 🔐 Data & Privacy

For development, testing, and demonstration:

- Only **synthetic or anonymised data** is used.
- No real personal or sensitive evidence is required.
- The project does not depend on real-world case files.
- The prototype is designed to demonstrate the concept of digital evidence integrity in a simple and understandable way.

## 🎯 Hackathon Context

**Hackathon:** ICSC 2026 Universities Hackathon  
**Track:** H — Proving Digital Evidence Has Not Been Changed  
**Team:** NurGuard AI — An-Nahda Labs

NurGuard AI focuses on the challenge of maintaining confidence in the integrity of digital evidence after collection.

The project demonstrates how basic cryptographic hashing, custody records, and offline-first design can be combined into a practical prototype.

## 📌 Project Status

**Status:** Hackathon Prototype

NurGuard AI is an ongoing prototype. Future development could include stronger audit trails, improved evidence metadata, role-based access, exportable reports, additional verification methods, and integration with more formal digital-forensics workflows.

