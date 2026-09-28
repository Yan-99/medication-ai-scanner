# AI Medication Verification System

An AI-powered web application designed to assist healthcare professionals with medication verification by comparing **physical medication packaging** against a **prescription/cartfill label**.

The system uses computer vision to extract medication information from both images, compares the medication name and strength, and records the verification result in a secure database for audit and review.

> **⚠️ Important:** This application is a prototype and is intended only as a verification aid. It does **not** replace professional clinical judgment, pharmacist verification, or institutional medication safety procedures.

---

## ✨ Features

### 📷 Image-Based Medication Verification

* Capture medication packaging using a device camera
* Capture prescription/cartfill label using the same camera
* Rear-facing camera support for mobile devices
* Temporary image previews before verification
* Automatic camera shutdown after capture

### 🤖 AI-Powered Comparison

The application sends both images to an OpenAI vision model to identify:

* Medication name
* Medication strength
* Prescription/label medication name
* Prescription/label strength
* Match status
* Confidence level
* Explanation for the result

The system is instructed to avoid guessing when information is unclear or unreadable.

### 🗄️ Audit Trail

Verification results are stored in a Supabase PostgreSQL database, including:

* Staff ID
* Date and time
* Medication name
* Medication strength
* Label medication name
* Label strength
* Match result
* Confidence
* Verification reason

### 📊 Scan History

Users can review previous verification records through the built-in Scan History interface.

Features include:

* Search by Staff ID or medication
* Filter by MATCH / DO NOT MATCH
* View verification details
* Display latest verification records
* Responsive interface for desktop and mobile

---

## 🏗️ Architecture

```text
┌─────────────────────────────┐
│          Browser            │
│                             │
│  Staff ID                   │
│  Medication Image           │
│  Prescription Label Image   │
└──────────────┬──────────────┘
               │
               │ POST /verify
               ▼
┌─────────────────────────────┐
│      Flask Backend          │
│        on Vercel            │
└──────────────┬──────────────┘
               │
               │ Image analysis
               ▼
┌─────────────────────────────┐
│      OpenAI Vision Model    │
│                             │
│  Medication extraction      │
│  Name + strength comparison │
│  Confidence assessment      │
└──────────────┬──────────────┘
               │
               │ Structured result
               ▼
┌─────────────────────────────┐
│     Supabase PostgreSQL     │
│                             │
│      scan_records           │
└──────────────┬──────────────┘
               │
               │ GET /history
               ▼
┌─────────────────────────────┐
│       Scan History UI       │
└─────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Technology              | Purpose                               |
| ----------------------- | ------------------------------------- |
| HTML / CSS / JavaScript | Frontend interface                    |
| Flask                   | Python backend/API                    |
| OpenAI API              | AI-powered image analysis             |
| Supabase                | PostgreSQL database and audit records |
| Vercel                  | Application deployment                |
| GitHub                  | Source code management                |

---

## 📁 Project Structure

```text
project/
│
├── api/
│   ├── index.py
│   └── templates/
│       └── index.html
│
├── requirements.txt
├── vercel.json
└── README.md
```

### `api/index.py`

Contains the Flask backend, including:

* `/` — serves the application
* `/verify` — processes medication verification requests
* `/history` — retrieves verification history
* OpenAI API integration
* Supabase database integration

### `api/templates/index.html`

Contains the frontend application, including:

* Staff ID entry
* Camera controls
* Medication image capture
* Prescription label capture
* Verification results
* Scan History
* Search and filtering
* Responsive styling

### `vercel.json`

Configures the Flask application for deployment on Vercel.

### `requirements.txt`

Contains the Python dependencies required by the application.

---

## 🔄 Verification Workflow

1. **Enter Staff ID**
2. **Capture medication packaging**
3. **Capture prescription/cartfill label**
4. **Click Verify**
5. Images are sent to the Flask backend
6. The backend sends the images to the OpenAI vision model
7. The AI extracts and compares medication information
8. The verification result is returned to the frontend
9. The result is recorded in Supabase
10. The record becomes available in Scan History

---

## 🧠 Verification Logic

The AI compares both:

### Medication Name

```text
Medication packaging
        ↓
Medication name
        ↕
Prescription label
        ↓
Medication name
```

### Medication Strength

```text
Medication packaging
        ↓
Medication strength
        ↕
Prescription label
        ↓
Medication strength
```

A **MATCH** requires both the medication name and strength to correspond.

If relevant information cannot be reliably identified, the system is instructed not to guess.

---

## 🔐 Environment Variables

The following environment variables are required:

```text
OPENAI_API_KEY
SUPABASE_URL
SUPABASE_KEY
```

### Example

```text
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_server_side_supabase_key
```

> **Never commit API keys, Supabase secret keys, or other credentials to GitHub.**

The Supabase server-side key is used only by the Flask backend and should **never** be exposed in frontend JavaScript.

---

## 🗃️ Database Schema

The application uses a Supabase table called `scan_records`.

```sql
create table public.scan_records (
  id bigint generated by default as identity primary key,

  staff_id text not null,

  created_at timestamptz not null default now(),

  medication_name text,
  medication_strength text,

  label_name text,
  label_strength text,

  match boolean,

  confidence text,

  reason text
);
```

Row Level Security (RLS) is enabled on the table.

Database access is performed by the backend rather than directly from the browser.

---

## 🚀 Deployment

The application can be deployed using Vercel.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Add the following variables to your local environment or Vercel project:

```text
OPENAI_API_KEY
SUPABASE_URL
SUPABASE_KEY
```

### 4. Run locally

```bash
flask --app api/index.py run
```

The application should then be available locally.

### 5. Deploy to Vercel

Connect the GitHub repository to Vercel and configure the required environment variables.

The included `vercel.json` configures the Flask application for deployment.

---

## 🔒 Privacy & Security Considerations

The application is designed so that:

* API keys remain on the backend
* Supabase credentials are not exposed to the frontend
* Captured images are held temporarily in the webpage during verification
* Captured images are not saved to `localStorage`
* Captured images are not saved to `sessionStorage`
* Captured images are not saved as downloadable files
* Verification results are stored as audit records in the database

However, this prototype should undergo additional security, privacy, and clinical governance review before being used with real patient data or in a production healthcare environment.

---

## ⚠️ Limitations

This application is an experimental/prototype system and has several limitations.

### Image Quality

Performance may be affected by:

* Blurry images
* Poor lighting
* Glare
* Obstructed packaging
* Small or unreadable text
* Partially visible labels

### AI Limitations

AI-generated results may contain errors. The system should therefore not be treated as an independent medication dispensing or verification system.

### Clinical Use

This application does not replace:

* Pharmacist verification
* Prescription review
* Medication reconciliation
* Institutional medication safety procedures
* Clinical judgment

Any uncertain or unexpected result should be independently verified by an appropriately qualified healthcare professional.

---

## 🔮 Future Improvements

Potential future development includes:

* [ ] User authentication
* [ ] Role-based access control
* [ ] Staff-specific scan history
* [ ] Administrator dashboard
* [ ] Improved handling of uncertain/ambiguous results
* [ ] Human confirmation workflow for low-confidence results
* [ ] Enhanced medication identification
* [ ] Barcode/QR code scanning
* [ ] Medication database integration
* [ ] Advanced audit logging
* [ ] Scan statistics and analytics
* [ ] Improved accessibility
* [ ] Automated test cases
* [ ] Additional security and privacy controls
* [ ] Clinical validation

---

## 📌 Project Status

**Prototype / Proof of Concept**

The current version demonstrates an end-to-end workflow for:

```text
Medication Image
       +
Prescription Label Image
       ↓
   AI Analysis
       ↓
Medication Comparison
       ↓
 Verification Result
       ↓
 Supabase Audit Record
       ↓
   Scan History
```

Further validation, security review, and clinical governance would be required before considering deployment in a real healthcare environment.

---

## 👤 Author

Developed as an exploration of the use of **AI, computer vision, and web technologies to support medication verification workflows**.

---

## 📄 Disclaimer

This project is provided for educational and prototyping purposes.

It is not a medical device and should not be used as the sole basis for medication dispensing, administration, prescribing, or other clinical decisions.
