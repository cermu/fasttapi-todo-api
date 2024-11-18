from celery import Celery
from .mail import mail, create_message
from .config import settings
from asgiref.sync import async_to_sync


celery_app = Celery(
    backend=settings.CELERY_RESULT_BACKEND,
    broker=settings.CELERY_BROKER_URL,
    broker_connection_retry_on_startup=True
)

@celery_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    message = create_message(recipients=recipients, subject=subject, body=body)
    async_to_sync(mail.send_message)(message)
    print("Email sent successfully by Celery task")

