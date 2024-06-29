from django.db import models
from django.conf import settings


class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    email = models.EmailField()
    credentials = models.JSONField()

    class Meta:
        constraints = [
            # Each email can only be added once by each user.
            models.UniqueConstraint(
fields=["user", "email"],
                name="unique_emails_per_user",
            )
        ]


class Message(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    subject = models.CharField(max_length=255)
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField()
    body = models.TextField()
    attachments = models.FileField(
        upload_to="attachments/%Y/%m/%d/",
        blank=True,
        null=True,
    )
