from content_profiles.models import ContentProfile
from user_accounts.account_model import GuestSession
from django.db import models

class PCUStatus(models.Model):
    code = models.TextField(db_column = "CODE")
    description = models.TextField(db_column = "DESCRIPTION")
    
    class Meta:
        db_table = "T_PCU_STATUS"

class PCU(models.Model):
    profile = models.ForeignKey(ContentProfile, editable=False, db_column="PROFILE_ID")
    publicKey = models.TextField(db_column="PUBLIC_KEY")
    url = models.URLField(db_column="URL")
    pcuIdentifier = models.TextField(db_column="PCU_IDENTIFIER")
    created = models.DateTimeField(auto_now = True, db_column = "CREATED")
    modified = models.DateTimeField(editable=False, null = True, db_column = "MODIFIED")
    status = models.ForeignKey(PCUStatus, db_column = "STATUS_ID")
    
    class Meta:
        db_table = "T_PCU"
        
class PCUAnalytics(models.Model):
    #id = models.IntegerField(db_column = "ID", primary_key = True)
    pcu = models.ForeignKey(PCU, editable=False, db_column="PCU_ID")
    hour = models.DateTimeField(db_column="HOUR")
    overlayOpenClicks = models.IntegerField(db_column="OVERLAY_OPEN_CLICKS")
    acceptClicks = models.IntegerField(null = True, db_column="ACCEPT_CLICKS")
    moreInformationClicks = models.IntegerField(null = True, db_column="MORE_INFORMATION_CLICKS")
    declineClicks = models.IntegerField(null = True, db_column="DECLINE_CLICKS")
    
    class Meta:
        db_table = "T_PCU_ANALYTICS"

class PCUAction(models.Model):
    code = models.TextField(db_column = "CODE")
    description = models.TextField(db_column = "DESCRIPTION")

    class Meta:
        db_table = "T_PCU_INTERACTION_ACTION"

class PCUInteraction(models.Model):
    pcu = models.ForeignKey(PCU, editable=False, db_column="PCU_ID")
    interactionTime = models.DateTimeField(auto_now = True, db_column="INTERACTION_TIME")
    action = models.ForeignKey(PCUAction, db_column = "ACTION_ID")
    session = models.ForeignKey(GuestSession, db_column = "SESSION_IDENT")
    
    class Meta:
        db_table = "T_PCU_INTERACTION"
        
class PCUInteractionData(models.Model):
    interaction = models.ForeignKey(PCUInteraction, db_column = "PCU_INTERACTION_ID")
    httpHeaders = models.TextField(db_column = "HTTP_HEADERS")
    
    class Meta:
        db_table = "T_PCU_INTERACTION_DATA"
    