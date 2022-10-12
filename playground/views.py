from django.shortcuts import render
from store.models import *


def say_hello(request):
    return render(request, 'hello.html', {'name': 'Solomon'})
