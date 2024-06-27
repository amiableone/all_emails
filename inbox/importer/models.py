from django.db import models


class Account(models.Model):
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)


class Message(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField()
    body = models.TextField()
    attachments = models.FileField(
        upload_to="attachments/%Y/%m/%d/",
        blank=True,
        null=True,
    )
