from django.db import models
from django.conf import settings
class Schedule(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True,related_name="course_schedule")
    browser_key=models.CharField(max_length=64,unique=True)
    state=models.JSONField(default=dict)
    revision=models.PositiveIntegerField(default=0)
