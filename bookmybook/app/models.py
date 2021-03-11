from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import binascii
import os

class Token(models.Model):
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super(Token, self).save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __unicode__(self):
        return self.token


class Pin(models.Model):
	user_id = models.IntegerField()
	pin = models.IntegerField()