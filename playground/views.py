from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import requests
# from .tasks import send_feedback_email_task

# executing task with celery:
# def say_hello(request):
#     send_feedback_email_task.delay(
#         'snnbotchway@gmail.com',
#         'Where the party dey today?'
#     )
#     return render(request, 'hello.html', {'name': 'Solomon'})

# caching function based view
# @cache_page(60 * 5)  # caching with 5 mins expiry
# def say_hello(request):
#     response = requests.get('https://httpbin.org/delay/2').json()
#     return render(request, 'hello.html', {'name': response})


# caching class based view
class SayHello(APIView):
    @method_decorator(cache_page(20))  # caching with 20 secs expiry
    def get(self, request):
        response = requests.get('https://httpbin.org/delay/2').json()
        return render(request, 'hello.html', {'name': response})
