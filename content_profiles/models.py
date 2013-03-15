from django.contrib.auth.models import User
from django.db import models

class ContentProfileStatus(models.Model):
    code = models.TextField(db_column = "CODE")
    description = models.TextField(db_column = "DESCRIPTION")
    
    class Meta:
        db_table = "T_PROFILE_STATUS"

class ContentProfile(models.Model):
    name = models.CharField(max_length=255, editable=False, db_column = "TITLE") #required=False,
    created_by = models.ForeignKey(User, editable=False, db_column = "USER_ID") 
    url = models.URLField(db_column = "URL")
    created_date = models.DateTimeField(auto_now=True, editable=False, db_column = "CREATED")
    deleted_date = models.DateTimeField(auto_now=False, editable=False, db_column = "DELETED")
    #status = models.ForeignKey(ContentProfileStatus, db_column = "STATUS_ID")
    status = models.IntegerField(db_column = "STATUS_ID")
    privateKey = models.TextField(editable=False, db_column = "PRIVATE_KEY")
    
    class Meta:
        db_table = "T_PROFILE"
