# Emailpilot 

**A Python-based email automation tool developed during my virtual internship at Syntecxhub.**

## About the Project

Emailpilot is an email automation project I developed as part of my virtual internship at **Syntecxhub**. The goal was to simplify the process of sending personalized emails to multiple recipients while making the workflow more organized and reliable.

The application reads recipient information from a CSV file, generates personalized emails, supports file attachments, and allows users to preview and approve messages before sending them. It also includes email format validation, retry logic, logging, and CSV delivery reports to help track the results.

Through this project, I gained practical experience applying Python to a real-world automation task while improving my understanding of email handling, error management, environment variables, and version control.

## Features

- **Personalized emails:** Generates customized messages using each recipient's name.
- **CSV recipient management:** Reads names and email addresses from a CSV file.
- **Email previews:** Displays message details before sending.
- **Approval workflow:** Allows users to approve, skip, or stop email processing.
- **File attachments:** Attaches files from the designated attachments folder.
- **Email validation:** Checks email address formatting before processing.
- **Retry logic:** Retries email sending when supported attempts fail.
- **Logging:** Records application activity and errors for troubleshooting.
- **Delivery reports:** Generates CSV reports containing recipient details, statuses, timestamps, and attempt information.
- **Test mode:** Simulates sending so the workflow can be tested without delivering real emails.

## Technologies Used

- Python
- `smtplib` and SMTP
- `email.message.EmailMessage`
- `python-dotenv`
- CSV file handling
- Logging and exception handling
- Git and GitHub

## Project Structure

```text
Emailpilot/
├── attachments/
│   └── sample.txt
├── logs/                    # Generated logs
├── reports/                 # Generated delivery reports
├── .env                     # Local credentials
├── .gitignore
├── main.py
├── recipients.csv           # Local recipient list
├── recipients.example.csv   # Example CSV format
├── requirements.txt
└── README.md
```

Sensitive and generated files are excluded from version control through `.gitignore`.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/Emailpilot.git
cd EmailPilot
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```dotenv
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

Use a Gmail App Password where supported, rather than your regular Gmail password. Never commit your `.env` file or share your credentials publicly.

### 5. Prepare the recipient list

Create a `recipients.csv` file:

```csv
name,email
Jane Example,jane@example.com
John Example,john@example.com
```

Replace the examples with recipient information you are authorized to use.

### 6. Add attachments

Place any files you want to attach inside the `attachments/` folder.

### 7. Run the application

```bash
python main.py
```

Review each email preview and follow the approval prompt in the terminal.

## Testing and Safety

Emailpilot includes a configurable test mode controlled by `TEST_MODE` in `main.py`.

- `TEST_MODE = True`: Simulates sending without delivering real emails.
- `TEST_MODE = False`: Sends approved emails through the configured SMTP service.

Before enabling real sending, verify the recipient list, configuration, and email previews. Keep credentials private and use test addresses you control when validating the application.

Email format validation does not verify that a mailbox exists. Similarly, SMTP acceptance does not guarantee final delivery to the recipient's inbox.

## Key Learnings

Developing Emailpilot during my virtual internship helped me gain practical experience with:

- Automating repetitive tasks using Python.
- Reading and processing CSV data.
- Creating email messages and working with SMTP.
- Managing application configuration through environment variables.
- Implementing validation, retry logic, and exception handling.
- Using logging and generating delivery reports.
- Managing source code with Git and GitHub.

## Future Improvements

Potential improvements include:

- Adding automated unit tests.
- Supporting HTML email templates.
- Improving attachment validation and error reporting.
- Making application settings configurable without editing the source code.
- Exploring OAuth 2.0 authentication.
- Improving reporting and delivery status tracking.

## About Me

**ANGELA MWAURA**

Computer Science Student | Aspiring AI/ML Engineer

GitHub: https://github.com/angiescodelife

## Acknowledgement

Developed as part of my virtual internship at **Syntecxhub**, where I applied my programming knowledge to build a practical email automation solution.

