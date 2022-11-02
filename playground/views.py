from django.shortcuts import render, HttpResponse
from django.core.mail import send_mail, BadHeaderError
from store.models import *
from .tasks import send_feedback_email_task


def say_hello(request):
    send_feedback_email_task.delay(
        'snnbotchway@gmail.com',
        'Where the party dey today?'
    )
    return render(request, 'hello.html', {'name': 'Solomon'})
