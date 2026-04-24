from celery import shared_task
import random
from .rate_limiter import allow_request


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_email_task(self, email):
    if not allow_request():
        raise Exception("Rate limit exceeded")

    if random.random() < 0.2:
        raise Exception("Simulated failure")

    print(f"Email sent to {email}")