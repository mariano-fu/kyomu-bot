from django.db import models

class Customer(models.Model):
    platform = models.CharField(max_length=20)
    user_id  = models.CharField(max_length=100, unique=True)

class ChatMessage(models.Model):
    customer  = models.ForeignKey(Customer, on_delete=models.CASCADE)
    inbound   = models.BooleanField()
    text      = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
