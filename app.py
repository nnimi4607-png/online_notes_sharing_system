from flask import Flask, jsonify, request, send_file, render_template
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io, datetime, json

app = Flask(__name__)

# ── Shared notes store (in-memory) ─────────────────────────────────────────
NOTES = [
    {"id":1,"userId":1,"title":"Calculus: Limits & Continuity","subject":"Mathematics",
     "desc":"Complete notes on limits, continuity theorems, L'Hôpital's rule, and epsilon-delta proofs. Includes worked examples and practice problems from Stewart Calculus.",
     "tags":["calculus","limits","continuity"],"format":"PDF","size":"2.4 MB",
     "date":"2024-05-10","downloads":134,"likes":48,"rating":4.8,"ratingCount":21,
     "comments":[{"user":"Priya S.","text":"Amazing notes, very detailed!","date":"2024-05-12"}]},

    {"id":2,"userId":2,"title":"Organic Chemistry: Reaction Mechanisms","subject":"Chemistry",
     "desc":"Detailed walkthrough of SN1, SN2, E1, E2 mechanisms with arrow-pushing diagrams. Covers nucleophiles, leaving groups, and stereochemistry.",
     "tags":["organic","mechanisms","stereochemistry"],"format":"PDF","size":"3.1 MB",
     "date":"2024-05-08","downloads":98,"likes":35,"rating":4.6,"ratingCount":15,
     "comments":[]},

    {"id":3,"userId":1,"title":"Data Structures & Algorithms","subject":"Computer Science",
     "desc":"Arrays, Linked Lists, Trees, Graphs, Sorting algorithms (QuickSort, MergeSort) with Big-O complexity analysis and Python implementations.",
     "tags":["DSA","python","algorithms","complexity"],"format":"PDF","size":"1.8 MB",
     "date":"2024-05-05","downloads":210,"likes":76,"rating":4.9,"ratingCount":34,
     "comments":[{"user":"Rahul M.","text":"Best DSA notes I've found!","date":"2024-05-07"}]},

    {"id":4,"userId":3,"title":"Thermodynamics Laws & Cycles","subject":"Physics",
     "desc":"All four laws of thermodynamics, Carnot cycle, Otto cycle, entropy, enthalpy, and Gibbs free energy with solved numerical problems.",
     "tags":["thermodynamics","physics","entropy"],"format":"PDF","size":"2.9 MB",
     "date":"2024-04-28","downloads":67,"likes":22,"rating":4.4,"ratingCount":10,
     "comments":[]},

    {"id":5,"userId":2,"title":"Indian Constitution & Polity","subject":"Political Science",
     "desc":"Preamble, Fundamental Rights, Directive Principles, Parliament structure, judicial review, and landmark Supreme Court judgments.",
     "tags":["constitution","polity","UPSC"],"format":"PDF","size":"4.2 MB",
     "date":"2024-04-20","downloads":183,"likes":61,"rating":4.7,"ratingCount":27,
     "comments":[]},

    {"id":6,"userId":3,"title":"Machine Learning Fundamentals","subject":"Computer Science",
     "desc":"Supervised vs unsupervised learning, regression, classification, clustering, neural networks, bias-variance tradeoff, and cross-validation techniques.",
     "tags":["ML","AI","neural-networks","python"],"format":"PDF","size":"3.5 MB",
     "date":"2024-05-01","downloads":156,"likes":54,"rating":4.8,"ratingCount":19,
     "comments":[]}
]

USERS = {
    1: {"name": "Aarav Sharma",   "email": "aarav@example.com",  "role": "student"},
    2: {"name": "Priya Singh",    "email": "priya@example.com",  "role": "student"},
    3: {"name": "Rahul Mehta",    "email": "rahul@example.com",  "role": "student"},
}

next_id = [7]

# ── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/notes")
def get_notes():
    subject = request.args.get("subject", "")
    search  = request.args.get("search", "").lower()
    result  = NOTES[:]
    if subject and subject != "All":
        result = [n for n in result if n["subject"] == subject]
    if search:
        result = [n for n in result if
                  search in n["title"].lower() or
                  search in n["desc"].lower() or
                  any(search in t.lower() for t in n["tags"])]
    return jsonify(result)

@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json()
    note = {
        "id": next_id[0],
        "userId": data.get("userId", 1),
        "title":   data["title"],
        "subject": data["subject"],
        "desc":    data.get("desc", ""),
        "tags":    data.get("tags", []),
        "format":  "PDF",
        "size":    "—",
        "date":    datetime.date.today().isoformat(),
        "downloads": 0, "likes": 0,
        "rating": 0.0, "ratingCount": 0,
        "comments": []
    }
    NOTES.insert(0, note)
    next_id[0] += 1
    return jsonify(note), 201

@app.route("/api/notes/<int:nid>/like", methods=["POST"])
def like_note(nid):
    note = next((n for n in NOTES if n["id"] == nid), None)
    if not note:
        return jsonify({"error": "Not found"}), 404
    note["likes"] += 1
    return jsonify({"likes": note["likes"]})

@app.route("/api/notes/<int:nid>/comment", methods=["POST"])
def add_comment(nid):
    note = next((n for n in NOTES if n["id"] == nid), None)
    if not note:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    comment = {"user": data["user"], "text": data["text"],
               "date": datetime.date.today().isoformat()}
    note["comments"].append(comment)
    return jsonify(comment), 201

@app.route("/api/notes/<int:nid>/download")
def download_note(nid):
    note = next((n for n in NOTES if n["id"] == nid), None)
    if not note:
        return jsonify({"error": "Not found"}), 404
    note["downloads"] += 1
    pdf_bytes = generate_pdf(note)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{note['title'].replace(' ','_')}.pdf"
    )

# ── PDF Generator ────────────────────────────────────────────────────────────
ACCENT  = colors.HexColor("#6c63ff")
ACCENT2 = colors.HexColor("#4f46e5")
LIGHT   = colors.HexColor("#ede9fe")
DARK    = colors.HexColor("#1a1a2e")
GRAY    = colors.HexColor("#6b7280")
BORDER  = colors.HexColor("#e5e7eb")

def generate_pdf(note):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=note["title"], author="NoteShare"
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Header banner ────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            f'<font color="white"><b>📚 NoteShare</b></font>',
            ParagraphStyle("hdr", fontSize=14, textColor=colors.white, alignment=TA_LEFT)
        ),
        Paragraph(
            f'<font color="white" size="9">{datetime.date.today().strftime("%d %B %Y")}</font>',
            ParagraphStyle("hdr_r", fontSize=9, textColor=colors.white, alignment=TA_RIGHT)
        )
    ]]
    header_tbl = Table(header_data, colWidths=["60%","40%"])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), ACCENT2),
        ("PADDING",    (0,0), (-1,-1), 12),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── Subject badge + title ─────────────────────────────────────────────
    story.append(Paragraph(
        f'<font color="#6c63ff" size="10"><b>[ {note["subject"].upper()} ]</b></font>',
        ParagraphStyle("subj", fontSize=10, textColor=ACCENT, spaceAfter=4)
    ))
    story.append(Paragraph(
        note["title"],
        ParagraphStyle("title", fontSize=22, fontName="Helvetica-Bold",
                       textColor=DARK, spaceAfter=8, leading=28)
    ))

    # ── Meta row ─────────────────────────────────────────────────────────
    user = USERS.get(note["userId"], {"name":"Unknown"})
    meta_data = [[
        Paragraph(f'<font color="#6b7280" size="9">👤 <b>{user["name"]}</b></font>',
                  ParagraphStyle("m", fontSize=9)),
        Paragraph(f'<font color="#6b7280" size="9">📅 {note["date"]}</font>',
                  ParagraphStyle("m", fontSize=9, alignment=TA_CENTER)),
        Paragraph(f'<font color="#6b7280" size="9">⬇ {note["downloads"]} downloads   ❤ {note["likes"]} likes</font>',
                  ParagraphStyle("m", fontSize=9, alignment=TA_RIGHT)),
    ]]
    meta_tbl = Table(meta_data, colWidths=["33%","34%","33%"])
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT),
        ("PADDING",    (0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=0.4*cm))

    # ── Description ──────────────────────────────────────────────────────
    story.append(Paragraph("📋 Description",
        ParagraphStyle("sec_head", fontSize=13, fontName="Helvetica-Bold",
                       textColor=ACCENT, spaceBefore=4, spaceAfter=6)))
    story.append(Paragraph(note["desc"],
        ParagraphStyle("body", fontSize=11, leading=17, textColor=DARK,
                       spaceAfter=0.4*cm)))

    # ── Tags ─────────────────────────────────────────────────────────────
    if note.get("tags"):
        story.append(Paragraph("🏷 Tags",
            ParagraphStyle("sec_head2", fontSize=13, fontName="Helvetica-Bold",
                           textColor=ACCENT, spaceAfter=6)))
        tag_str = "   ".join(f"  {t}  " for t in note["tags"])
        story.append(Paragraph(tag_str,
            ParagraphStyle("tags", fontSize=10, textColor=colors.HexColor("#5b21b6"),
                           backColor=LIGHT, borderPadding=6, spaceAfter=0.4*cm)))

    # ── Stats table ───────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=0.4*cm))
    story.append(Paragraph("📊 Statistics",
        ParagraphStyle("sec_head3", fontSize=13, fontName="Helvetica-Bold",
                       textColor=ACCENT, spaceAfter=8)))

    rating_str = f"{note['rating']:.1f} / 5.0  ({note['ratingCount']} ratings)" if note['ratingCount'] else "No ratings yet"
    stats_data = [
        ["Metric", "Value"],
        ["Downloads",    str(note["downloads"])],
        ["Likes",        str(note["likes"])],
        ["Rating",       rating_str],
        ["File Format",  note.get("format","PDF")],
        ["File Size",    note.get("size","—")],
        ["Upload Date",  note["date"]],
    ]
    stats_tbl = Table(stats_data, colWidths=["40%","60%"])
    stats_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0),  ACCENT2),
        ("TEXTCOLOR",    (0,0), (-1,0),  colors.white),
        ("FONTNAME",     (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 10),
        ("PADDING",      (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
        ("GRID",         (0,0), (-1,-1), 0.5, BORDER),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(stats_tbl)

    # ── Comments ──────────────────────────────────────────────────────────
    if note.get("comments"):
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=0.4*cm))
        story.append(Paragraph("💬 Comments",
            ParagraphStyle("sec_head4", fontSize=13, fontName="Helvetica-Bold",
                           textColor=ACCENT, spaceAfter=8)))
        for c in note["comments"]:
            c_data = [[
                Paragraph(f'<b>{c["user"]}</b>  <font color="#6b7280" size="8">{c["date"]}</font>',
                          ParagraphStyle("cu", fontSize=10)),
                Paragraph(c["text"],
                          ParagraphStyle("ct", fontSize=10, leading=14))
            ]]
            c_tbl = Table(c_data, colWidths=["35%","65%"])
            c_tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0,0), (-1,-1), colors.white),
                ("LEFTPADDING", (0,0), (0,-1),  10),
                ("GRID",        (0,0), (-1,-1),  0.5, BORDER),
                ("ROUNDEDCORNERS", [6]),
            ]))
            story.append(c_tbl)
            story.append(Spacer(1, 0.2*cm))

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=0.3*cm))
    story.append(Paragraph(
        '<font color="#6b7280" size="8">Generated by NoteShare — Online Notes Sharing System &nbsp;|&nbsp; '
        f'Downloaded on {datetime.date.today().strftime("%d %B %Y")}</font>',
        ParagraphStyle("footer", fontSize=8, textColor=GRAY, alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()


if __name__ == "__main__":
    print("=" * 52)
    print("  NoteShare running →  http://localhost:5000")
    print("=" * 52)
    app.run(debug=True, port=5000)
