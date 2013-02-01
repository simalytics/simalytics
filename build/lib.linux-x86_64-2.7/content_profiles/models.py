from django.contrib.auth.models import User
from django.db import models

class ContentProfile(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    created_by = models.ForeignKey(User, editable=False)
    created_date = models.DateField(auto_now=True, editable=False)
    content = models.TextField()
