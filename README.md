# 📚 NoteShare — Online Notes Sharing System

A full-stack web app where students can browse, share, and **download notes as real PDFs**.

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install flask reportlab
```

### 2. Run the server
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## 📁 Project Structure
```
noteshare/
├── app.py              ← Flask backend + PDF generator
├── requirements.txt    ← Python dependencies
└── templates/
    └── index.html      ← Full frontend (HTML/CSS/JS)
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Browse Notes** | Filter by subject, sort by downloads/likes/rating |
| **Search** | Full-text search across title, description, tags |
| **Download PDF** | Real styled PDF generated on-the-fly by the server |
| **Like Notes** | Like any note (login required) |
| **Rate Notes** | 5-star rating system |
| **Comments** | Add comments to any note (login required) |
| **Upload Notes** | Share your own notes (login required) |
| **Dark Mode** | Toggle light/dark theme |
| **Auth** | Login / Register system |

---

## 🔑 Demo Accounts

| Name | Email | Password |
|---|---|---|
| Aarav Sharma | aarav@example.com | demo123 |
| Priya Singh | priya@example.com | demo123 |
| Rahul Mehta | rahul@example.com | demo123 |

---

## 🖨 PDF Contents

Each downloaded PDF includes:
- Styled header banner with NoteShare branding
- Note title, subject badge, upload date
- Author info, download count, likes
- Full description
- Tags
- Statistics table
- Comments (if any)
- Footer with download timestamp

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/notes` | List notes (supports `?subject=` and `?search=`) |
| POST | `/api/notes` | Create a new note |
| POST | `/api/notes/<id>/like` | Like a note |
| POST | `/api/notes/<id>/comment` | Add a comment |
| GET | `/api/notes/<id>/download` | **Download PDF** |
