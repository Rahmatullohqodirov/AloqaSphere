from django.db import models
from django.conf import settings

class ReportModel(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='connection')
    title = models.CharField(max_length=200)
    about_report = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title