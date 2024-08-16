
import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(default=datetime.date.today)
    profile_picture = models.ImageField(upload_to='profile_pictures/')
    
    