# app/email_tasks.py
import logging,time

def send_email(to: str, subject: str, body: str):
    logging.info(f"[EMAIL SENT] To={to}, Subject={subject}")
    time.sleep(5)
    print("Email sent")
