
from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import urlparse
import re
import sqlite3
from datetime import datetime

app = Flask(__name__)
def init_db():
    connection = sqlite3.connect("scamshield.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_type TEXT,
            scanned_text TEXT,
            risk TEXT,
            reasons TEXT,
            scanned_at TEXT
        )
    """)

    connection.commit()
    connection.close()


init_db()

def check_scam(text, scan_type):
    text = text.strip()
    reasons = []
    score = 0

    if not text:
        return "No input", ["Please enter a link or message."], "Unknown"

    if scan_type == "url":
        parsed = urlparse(text)
        host = parsed.hostname or ""

        if parsed.scheme not in ("http", "https") or not host:
            reasons.append("The URL format is invalid or incomplete.")
            score += 2

        if "@" in text:
            reasons.append("The URL contains an @ symbol.")
            score += 2

        if host.startswith("xn--") or ".xn--" in host:
            reasons.append("The domain uses an encoded international name.")
            score += 2

        if re.search(r"\d{5,}", host):
            reasons.append("The domain contains a long sequence of digits.")
            score += 1

        if parsed.scheme == "http" and host:
            reasons.append("The connection does not use HTTPS.")
            score += 1

        if not reasons:
            reasons.append(
                "No suspicious patterns from the basic checks were found."
            )

    else:
        patterns = [
            (r"\b(otp|password|pin)\b", "Requests an OTP, password or PIN."),
            (r"\b(prize|winner|won|lottery)\b",
             "Mentions a prize or lottery."),
            (r"\b(urgent|immediately|act now)\b",
             "Uses urgent or pressure-based language."),
            (r"\b(pay now|send money|bank details)\b",
             "Requests money or financial details."),
            (r"https?://\S+", "Contains a web link."),
        ]

        for pattern, reason in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                reasons.append(reason)
                score += 2

        if not reasons:
            reasons.append("No suspicious phrases from the basic checks were found.")

    if score >= 4:
        risk = "High"
    elif score >= 2:
        risk = "Medium"
    else:
        risk = "Low"

    return risk, reasons, "Completed"



@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        scan_type = request.form.get("scan_type", "message")
        text = request.form.get("text", "").strip()

        if scan_type not in ("url", "message"):
            scan_type = "message"

        if text:
            risk, reasons, status = check_scam(text, scan_type)

            result = {
                "risk": risk,
                "reasons": reasons,
                "status": status,
                "input": text
            }

            connection = sqlite3.connect("scamshield.db")

            connection.execute(
                """INSERT INTO scan_history
                (scan_type, scanned_text, risk, reasons, scanned_at)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    scan_type,
                    text,
                    risk,
                    "; ".join(reasons),
                    datetime.now().strftime("%d-%m-%Y %H:%M")
                )
            )

            connection.commit()
            connection.close()

    connection = sqlite3.connect("scamshield.db")
    connection.row_factory = sqlite3.Row

    history = connection.execute(
        """SELECT * FROM scan_history
        ORDER BY id DESC LIMIT 10"""
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        result=result,
        history=history
    )

@app.route("/delete_scan/<int:scan_id>", methods=["POST"])
def delete_scan(scan_id):
    connection = sqlite3.connect("scamshield.db")

    connection.execute(
        "DELETE FROM scan_history WHERE id = ?",
        (scan_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("home"))


@app.route("/clear_history", methods=["POST"])
def clear_history():
    connection = sqlite3.connect("scamshield.db")

    connection.execute("DELETE FROM scan_history")

    connection.commit()
    connection.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)