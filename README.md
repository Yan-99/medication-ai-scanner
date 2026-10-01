# AI Medication Verification System

An AI-powered web application designed to assist healthcare professionals with medication verification by comparing **physical medication packaging** against a **prescription/cartfill label**.

The system provides two complementary verification workflows:

1. **AI Medication Verification** — uses images of medication packaging and a prescription/cartfill label for AI-assisted comparison.
2. **QR / Barcode Verification** — compares machine-readable medication product identifiers directly without using AI.

Verification results are recorded in Supabase for audit and review through a unified **Scan History** interface.

> **⚠️ Important:** This application is a prototype and is intended only as a verification aid. It does **not** replace professional clinical judgment, pharmacist verification, or institutional medication safety procedures.

---

## ✨ Features

### 🤖 AI Medication Verification

The AI workflow allows a staff member to:

1. Enter their Staff ID.
2. Capture an image of the medication packaging.
3. Capture an image of the prescription/cartfill label.
4. Submit both images for AI verification.
5. Receive a verification result.

The AI workflow extracts and compares:

* Medication name
* Medication strength
* Prescription/label medication name
* Prescription/label strength
* Match status
* Confidence level
* Explanation for the result

The system is instructed to avoid guessing when information is unclear or unreadable.

### 📷 Camera Capture

The AI verification workflow supports:

* Device camera access
* Rear-facing camera preference on mobile devices
* Separate medication and label capture stages
* Image previews
* Camera start/stop controls
* Automatic camera shutdown after capture
* Reset / Start New Verification workflow

### 📱 QR / Barcode Verification

The QR/barcode workflow provides a deterministic alternative when the medication and prescription/cartfill label contain the same product identifier.

It supports:

* 📷 Camera-based QR/barcode scanning
* 🔌 Physical barcode scanner input
* Switching between camera and barcode scanner modes
* Medication product ID capture
* Prescription/cartfill label product ID capture
* Direct product ID comparison
* MATCH / DO NOT MATCH results
* Audit-record storage

The QR/barcode workflow does **not** require OpenAI.

The comparison is performed directly:

```javascript
const match = medicationId === labelId;
```

This allows the application to use a deterministic comparison when a reliable machine-readable product identifier is available.

### 🗄️ Audit Trail

Verification results are stored in Supabase PostgreSQL.

AI verification records contain:

* Staff ID
* Date and time
* Medication name
* Medication strength
* Label medication name
* Label strength
* Match result
* Confidence
* Verification reason

QR/barcode verification records contain:

* Staff ID
* Date and time
* Medication product ID
* Label product ID
* Match result

### 📊 Unified Scan History

The application provides a unified Scan History interface for both AI and QR/barcode verification records.

Features include:

* AI and QR verification types
* Search by Staff ID or medication/product ID
* Filter by verification type
* Filter by MATCH / DO NOT MATCH
* View verification details
* Display recent verification records
* Responsive interface for desktop and mobile

AI and QR records remain stored in separate database tables while being combined by the backend for display.

---

## 🏗️ Architecture

```text
                              ┌──────────────────────┐
                              │       Browser        │
                              └──────────┬───────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
                    ▼                                         ▼
          🤖 AI Verification                         📱 QR / Barcode
                    │                                         │
                    │                                         │
          Medication Image                          Camera / Barcode
          Label Image                                Scanner Input
                    │                                         │
                    ▼                                         ▼
          POST /verify                              Product IDs
                    │                                         │
                    ▼                                         ▼
           Flask Backend                           Direct Comparison
             on Vercel                              ID === ID
                    │                                         │
                    ▼                                         │
            OpenAI Vision                                    │
                    │                                         │
                    └────────────────┬────────────────────────┘
                                     │
                                     ▼
                              Flask Backend
                                     │
                       ┌─────────────┴─────────────┐
                       │                           │
                       ▼                           ▼
                scan_records              qr_scan_records
                       │                           │
                       └─────────────┬─────────────┘
                                     │
                                     ▼
                              /history API
                                     │
                                     ▼
                            📋 Scan History UI
```

---

## 🛠️ Technology Stack

| Technology              | Purpose                               |
| ----------------------- | ------------------------------------- |
| HTML / CSS / JavaScript | Frontend interface                    |
| Flask                   | Python backend / API                  |
| OpenAI API              | AI-powered image analysis             |
| Supabase                | PostgreSQL database and audit records |
| Vercel                  | Application deployment                |
| `html5-qrcode`          | Camera-based QR/barcode scanning      |
| Git / GitHub            | Source code management                |

---

## 📁 Project Structure

A simplified project structure:

```text
project/
│
├── api/
│   └── index.py
│
├── templates/
│   ├── index.html
│   └── qr.html
│
├── requirements.txt
├── vercel.json
└── README.md
```

### `api/index.py`

Contains the Flask backend, including:

* `/` — serves the AI verification interface
* `/verify` — processes AI medication verification requests
* `/qr` — serves the QR/barcode verification interface
* `/qr-verify` — processes QR/barcode verification audit records
* `/history` — returns unified AI + QR history as JSON
* OpenAI API integration
* Supabase database integration

### `templates/index.html`

Contains:

* AI verification workflow
* Staff ID entry
* Camera controls
* Medication image capture
* Prescription label capture
* Verification results
* Application navigation
* Scan History
* Search and filtering
* Verification details
* Responsive styling

### `templates/qr.html`

Contains:

* QR/barcode verification workflow
* Staff ID entry
* Barcode scanner mode
* Camera scanner mode
* Medication product ID capture
* Prescription/cartfill label product ID capture
* Product ID comparison
* Verification result
* Audit-record submission

### `vercel.json`

Configures the Flask application for deployment on Vercel.

### `requirements.txt`

Contains the Python dependencies required by the application.

---

## 🧭 Application Navigation

The application currently provides three main areas:

```text
🤖 AI Verify
📱 QR Verify
📋 Scan History
```

### AI Verification

```text
/
```

### QR / Barcode Verification

```text
/qr
```

### Scan History

The Scan History interface is displayed through the main application page:

```text
/?view=history
```

The backend endpoint:

```text
/history
```

is intentionally kept as a **JSON API endpoint** and should not be changed into an HTML page.

---

## 🔄 AI Verification Workflow

```text
1. Enter Staff ID
        ↓
2. Capture medication packaging
        ↓
3. Capture prescription/cartfill label
        ↓
4. Click Verify
        ↓
5. Images sent to Flask backend
        ↓
6. Backend sends images to OpenAI Vision
        ↓
7. AI extracts medication information
        ↓
8. Medication name + strength comparison
        ↓
9. Verification result returned
        ↓
10. Result recorded in Supabase
        ↓
11. Record appears in Scan History
```

---

## 📱 QR / Barcode Verification Workflow

```text
1. Enter Staff ID
        ↓
2. Scan medication
        ↓
   ┌─────────────────────────────┐
   │ 🔌 Barcode Scanner | 📷 Camera │
   └─────────────────────────────┘
        ↓
3. Medication Product ID
        ↓
4. Scan prescription/cartfill label
        ↓
   ┌─────────────────────────────┐
   │ 🔌 Barcode Scanner | 📷 Camera │
   └─────────────────────────────┘
        ↓
5. Label Product ID
        ↓
6. Compare Product IDs
        ↓
7. MATCH / DO NOT MATCH
        ↓
8. Save audit record
        ↓
9. Record appears in Scan History
```

The two scanning stages can independently use either scanning method.

For example:

```text
Medication → Barcode Scanner
Label      → Camera
```

or:

```text
Medication → Camera
Label      → Barcode Scanner
```

---

## 🧠 AI Verification Logic

The AI compares two main pieces of information.

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

A **MATCH** requires the medication name and strength identified from the two sources to correspond according to the verification logic.

If relevant information cannot be reliably identified, the system is instructed not to guess.

---

## 🔢 QR / Barcode Verification Logic

Unlike the AI workflow, the QR/barcode workflow does not interpret the medication name or strength.

Instead, it compares the product identifiers directly:

```text
Medication Product ID
        ↓
        ===
        ↑
Label Product ID
```

For example:

```text
Medication: 1234567890
Label:      1234567890

→ MATCH
```

Where the identifiers differ:

```text
Medication: 1234567890
Label:      0987654321

→ DO NOT MATCH
```

This provides a deterministic comparison when the product identifiers are reliable.

---

## 🔌 Physical Barcode Scanner

Many USB barcode scanners behave like keyboard input.

The intended workflow is:

```text
Physical Scanner
      ↓
Types barcode into input field
      ↓
Scanner sends Enter
      ↓
Web application captures value
      ↓
Product ID recorded
```

The application therefore does not require a special browser API for basic keyboard-style barcode scanners.

Physical scanner hardware testing remains an important validation step before operational use.

---

## 📷 Camera Scanning

Camera-based QR/barcode scanning uses the `html5-qrcode` library.

The application prefers the device's environment-facing camera:

```javascript
{
  facingMode: "environment"
}
```

Medication and label scanning use separate scanner instances so that one camera workflow can be stopped before the next stage begins.

---

## 🗄️ Database Schema

The application uses two Supabase tables.

### AI verification records

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

### QR / barcode verification records

```sql
create table public.qr_scan_records (
  id bigint generated by default as identity primary key,
  created_at timestamptz not null default now(),
  staff_id text not null,
  medication_product_id text not null,
  label_product_id text not null,
  match boolean not null
);
```

The Flask `/history` endpoint retrieves records from both tables and converts them into a unified format for the frontend.

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

> **⚠️ Never commit API keys, Supabase secret keys, or other credentials to GitHub.**

The Supabase server-side key is used by the Flask backend and should never be exposed in frontend JavaScript.

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

After deployment, verify:

```text
/
 /qr
 /?view=history
```

---

## 🔒 Privacy & Security Considerations

The application is designed so that:

* API keys remain on the backend
* Supabase credentials are not exposed to the frontend
* Captured AI images are held temporarily in the webpage during verification
* Captured images are not intentionally saved to `localStorage`
* Captured images are not intentionally saved to `sessionStorage`
* Captured images are not intentionally saved as downloadable files
* AI verification results are stored as audit records
* QR/barcode verification results are stored as audit records

However, the prototype should undergo additional security, privacy, and clinical governance review before being used with real patient data or in a production healthcare environment.

Important areas for future review include:

* What information is transmitted to external AI services
* Data retention
* Access control
* Authentication
* Staff ID handling
* Audit-log access
* Patient-identifiable information
* Organisational policies
* Applicable Singapore healthcare and privacy requirements

---

## ⚠️ Limitations

This application is an experimental/prototype system.

### Image Quality

AI performance may be affected by:

* Blurry images
* Poor lighting
* Glare
* Obstructed packaging
* Small or unreadable text
* Partially visible labels

### AI Limitations

AI-generated results may contain errors.

The AI workflow should therefore not be treated as an independent medication dispensing or verification system.

### Barcode / QR Limitations

The deterministic workflow assumes that:

* The product identifier can be read successfully.
* The medication and label contain the intended identifiers.
* The identifiers are correctly associated with the products being compared.

A matching identifier does not by itself establish that every aspect of a medication order is clinically appropriate.

### Clinical Use

This application does not replace:

* Pharmacist verification
* Prescription review
* Medication reconciliation
* Institutional medication safety procedures
* Clinical judgment

Any uncertain or unexpected result should be independently verified by an appropriately qualified healthcare professional.

---

## 🧪 Testing

### AI Workflow

Test:

* Valid medication + matching label
* Medication + non-matching label
* Missing Staff ID
* Camera permissions
* Camera start / stop
* Reset / Start New Verification
* AI result saving
* Scan History display

### QR / Barcode Workflow

Test:

* Camera → Camera
* Barcode scanner → Barcode scanner
* Barcode scanner → Camera
* Camera → Barcode scanner
* Matching product IDs
* Non-matching product IDs
* Reset behaviour
* Audit record creation
* Scan History display

### Hardware Testing

Physical barcode scanner testing should be performed when scanner hardware is available.

---

## 🗺️ Development Roadmap

### Phase 1 — QR / Camera Verification

* [x] Camera-based QR/barcode scanning
* [x] Medication product ID capture
* [x] Prescription/cartfill label capture
* [x] Deterministic product ID comparison

### Phase 2 — QR Audit Logging

* [x] `/qr-verify` endpoint
* [x] `qr_scan_records` table
* [x] MATCH / DO NOT MATCH audit records

### Phase 3 — Unified Scan History

* [x] Combined AI + QR history
* [x] Search
* [x] Verification-type filter
* [x] Result filter
* [x] Details view

### Phase 3.5 — Navigation & Barcode Scanner Support

* [x] AI Verify navigation
* [x] QR Verify navigation
* [x] Scan History navigation
* [x] Camera / Barcode Scanner toggle
* [x] Barcode scanner keyboard-input workflow
* [ ] Physical scanner hardware testing

### Phase 4 — UI / UX Refinement

* [ ] Establish overall visual design system
* [ ] Improve AI verification interface
* [ ] Improve QR/barcode interface
* [ ] Improve Scan History interface
* [ ] Improve mobile responsiveness
* [ ] Accessibility refinement

### Future Development

* [ ] User authentication
* [ ] Role-based access control
* [ ] Staff-specific history
* [ ] Administrator dashboard
* [ ] Human confirmation workflow for uncertain AI results
* [ ] Medication database integration
* [ ] Advanced audit logging
* [ ] Scan statistics and analytics
* [ ] Automated test cases
* [ ] Additional security and privacy controls
* [ ] Clinical validation

---

## 💡 Design Philosophy

The application intentionally supports two different verification approaches.

### AI Verification

Useful when verification requires interpretation of medication packaging and prescription/label information.

```text
Images
  ↓
AI analysis
  ↓
Information extraction
  ↓
Comparison
  ↓
Verification result
```

### QR / Barcode Verification

Useful when both items contain a reliable machine-readable product identifier.

```text
Product ID
  ↓
Direct comparison
  ↓
Verification result
```

The deterministic workflow avoids introducing AI when a machine-readable identifier can provide a direct comparison.

---

## 📌 Project Status

**Prototype / Proof of Concept — Active Development**

The application currently demonstrates an end-to-end system containing:

```text
                 AI Workflow
                     │
Medication Image + Label Image
                     │
                     ▼
                 AI Analysis
                     │
                     ▼
              Verification Result
                     │
                     ▼
                Supabase Audit
                     │
                     │
                     ▼
               Scan History
                     ▲
                     │
              QR / Barcode
                     │
              Product IDs
                     │
                     ▼
             Direct Comparison
```

The core AI verification workflow, QR/camera verification workflow, audit logging, unified Scan History, application navigation, and barcode scanner interface have been implemented.

The next development stage is **Phase 4 — UI/UX refinement**, while physical barcode scanner testing will be performed when hardware is available.

---

## 👤 Author

Developed as an exploration of the use of **AI, computer vision, barcode technology, and web technologies to support medication verification workflows**.

---

## 📄 Disclaimer

This project is provided for educational and prototyping purposes.

It is not a medical device and should not be used as the sole basis for medication dispensing, administration, prescribing, or other clinical decisions.
