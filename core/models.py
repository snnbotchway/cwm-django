from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):   # Always instantiate with pass at the beginning of a project
    email = models.EmailField(unique=True)
