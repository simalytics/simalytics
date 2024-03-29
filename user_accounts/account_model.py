from django.db import models
from content_profiles.models import ContentProfile

class GuestSession(models.Model):
    startTime = models.DateTimeField(auto_now = True, db_column = "START_TIME")
    duration = models.IntegerField(null = True, db_column = "DURATION_MS")
    profile = models.ForeignKey(ContentProfile, editable = False, db_column = "PROFILE_ID")
    sourceIp = models.TextField(db_column = "SOURCE_IP")
    externalIdent = models.CharField(primary_key = True, max_length = 255, db_column = "EXTERN_IDENT")
    
    class Meta:
        db_table = "T_GUEST_SESSION"