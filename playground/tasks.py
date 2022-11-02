from time import sleep
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import HttpResponse
from celery import shared_task


@shared_task()
def send_feedback_email_task(email_address, message):
    sleep(20)  # Simulate expensive operation(s) that freeze Django
    try:
        send_mail(
            "Your Feedback",
            f"\t{message}\n\nThank you!",
            "support@example.com",
            [email_address],
            fail_silently=False,
        )
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
