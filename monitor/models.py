from django.db import models

# Create your models here.
from django.db import models

class APILog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    port = models.CharField(max_length=10, blank=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    token = models.CharField(max_length=512, blank=True, null=True)
    payload = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp} - {self.ip_address} - {self.endpoint}"
