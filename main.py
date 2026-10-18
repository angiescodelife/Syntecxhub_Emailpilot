import re
import csv
import logging
import os
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))

# =========================================================
# 1. CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

RECIPIENTS_FILE = BASE_DIR / "recipients.csv"
ATTACHMENTS_DIR = BASE_DIR / "attachments"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

MAX_RETRIES = 3
RETRY_DELAY = 3

# Keep True until Gmail is configured and real sending is intended.
TEST_MODE = False


# =========================================================
# 2. LOGGING AND REPORT SETUP
# =========================================================

LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            LOGS_DIR / "emailpilot.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = REPORTS_DIR / f"emailpilot_report_{run_id}.csv"

REPORT_FIELDS = [
    "timestamp",
    "name",
    "email",
    "status",
    "attempts",
    "details",
]


def write_report(name, email, status, attempts=0, details=""):
    """Append one recipient's outcome to this run's CSV report."""
    with REPORT_FILE.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=REPORT_FIELDS)

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "name": name,
            "email": email,
            "status": status,
            "attempts": attempts,
            "details": details,
        })


# =========================================================
# 3. CREATE A PERSONALIZED EMAIL
# =========================================================


def create_email(name, recipient_email):
    """Create a personalized email and safely add attachments."""

    message = EmailMessage()
    message["Subject"] = f"Hello, {name}!"
    message["From"] = EMAIL_ADDRESS
    message["To"] = recipient_email

    message.set_content(
        f"""Hi {name},

I hope you're doing well!

This is a personalized email sent using Emailpilot,
my Python email automation project.

Best regards,
Emailpilot
"""
    )

    # Validate the attachments folder
    if not ATTACHMENTS_DIR.exists():
        raise FileNotFoundError(
            f"Attachments folder not found: {ATTACHMENTS_DIR}"
        )

    if not ATTACHMENTS_DIR.is_dir():
        raise NotADirectoryError(
            f"Attachments path is not a folder: {ATTACHMENTS_DIR}"
        )

    # Attach each readable file
    for path in sorted(ATTACHMENTS_DIR.iterdir()):
        if path.name.startswith(".") or not path.is_file():
            continue

        try:
            with path.open("rb") as attachment:
                file_data = attachment.read()

            message.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=path.name,
            )

            logger.info("Attached file: %s", path.name)

        except OSError as error:
            logger.exception("Could not read attachment: %s", path.name)
            raise OSError(
                f"Could not read attachment '{path.name}': {error}"
            ) from error

    return message


# =========================================================
# 4. PREVIEW THE EMAIL
# =========================================================

def preview_email(message):
    """Display the message before asking for approval."""

    print("\n" + "=" * 55)
    print("                  EMAILPILOT PREVIEW")
    print("=" * 55)
    print(f"From: {message['From']}")
    print(f"To: {message['To']}")
    print(f"Subject: {message['Subject']}")
    print("\nMessage:")

    body = message.get_body(preferencelist=("plain",))

    if body is not None:
        print(body.get_content())
    else:
        print("[No plain-text body found.]")

    attachments = list(message.iter_attachments())
    print(f"\nAttachments: {len(attachments)}")

    for attachment in attachments:
        print(f"  - {attachment.get_filename()}")

    print("=" * 55)


# =========================================================
# 5. SEND EMAIL WITH RETRIES
# =========================================================

def send_email(message, recipient_email):
    """
    Return (success, attempts, details).

    In test mode, no connection to Gmail is made.
    """

    if TEST_MODE:
        logger.info(
            "[TEST MODE] Would send to %s | Subject: %s",
            recipient_email,
            message["Subject"],
        )
        return True, 0, "Simulated only; no email was sent"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with smtplib.SMTP(
                SMTP_SERVER,
                SMTP_PORT,
                timeout=30,
            ) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(message)

            logger.info("SMTP accepted email for %s", recipient_email)
            return True, attempt, "Accepted by SMTP server"

        except (smtplib.SMTPException, OSError) as error:
            logger.warning(
                "Attempt %d/%d failed for %s: %s",
                attempt,
                MAX_RETRIES,
                recipient_email,
                error,
            )

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return False, MAX_RETRIES, "All send attempts failed"


# =========================================================
# 6. PROCESS RECIPIENTS
# =========================================================

def main():
    """Preview, approve, process and report each recipient."""

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.error(
            "Set EMAIL_ADDRESS and EMAIL_PASSWORD in .env."
        )
        return

    if not RECIPIENTS_FILE.exists():
        logger.error("recipients.csv was not found.")
        return

    simulated_or_sent = 0
    failed = 0
    skipped = 0

    try:
        with RECIPIENTS_FILE.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames or not {
                "name", "email"
            }.issubset(set(reader.fieldnames)):
                logger.error("CSV must contain columns: name,email")
                return

            for row in reader:
                name = (row.get("name") or "").strip()
                email = (row.get("email") or "").strip()

                if not name or not email:
                    logger.warning("Skipping row with missing data.")
                    write_report(
                        name, email, "SKIPPED", 0,
                        "Missing name or email",
                    )
                    skipped += 1
                    continue

                if not is_valid_email(email):
                    logger.warning("Skipping row with invalid email: %s", email)
                    write_report(
                        name, email, "SKIPPED", 0,
                        "Invalid email format",
                    )
                    skipped += 1
                    continue

                try:
                    message = create_email(name, email)
                    preview_email(message)

                    choice = input(
                        "\nApprove this email? "
                        "[Y]es / [N]o / [Q]uit: "
                    ).strip().lower()

                    if choice == "q":
                        logger.info("Processing stopped by user.")
                        break

                    if choice == "n":
                        write_report(
                            name, email, "SKIPPED", 0,
                            "Declined by user",
                        )
                        logger.info("Skipped %s", email)
                        skipped += 1
                        continue

                    if choice != "y":
                        write_report(
                            name, email, "SKIPPED", 0,
                            "Invalid approval choice",
                        )
                        logger.warning("Skipped invalid choice for %s", email)
                        skipped += 1
                        continue

                    success, attempts, details = send_email(
                        message, email
                    )

                    if success:
                        status = "SIMULATED" if TEST_MODE else "SMTP_ACCEPTED"
                        simulated_or_sent += 1
                    else:
                        status = "FAILED"
                        failed += 1

                    write_report(
                        name, email, status, attempts, details
                    )

                except (OSError, ValueError, smtplib.SMTPException) as error:
                    logger.exception("Error processing %s", email)
                    write_report(
                        name, email, "FAILED", 0, str(error)
                    )
                    failed += 1

    except OSError as error:
        logger.exception("Could not read recipients.csv: %s", error)
        return

    print("\n" + "=" * 45)
    print("             EMAILPILOT SUMMARY")
    print("=" * 45)
    print(f"Simulated / SMTP accepted: {simulated_or_sent}")
    print(f"Failed:                    {failed}")
    print(f"Skipped:                   {skipped}")
    print(f"Test mode:                 {TEST_MODE}")
    print(f"Report: {REPORT_FILE.relative_to(BASE_DIR)}")
    print("=" * 45)

    logger.info("Report saved to %s", REPORT_FILE)


# =========================================================
# 7. RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    main()
