from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager
from datetime import datetime

class CustomUser(AbstractUser):
    phonenumber = models.CharField(max_length=15, unique=True, blank=False, null=False)
    location=models.BooleanField(default=False)
    USERNAME_FIELD = 'phonenumber'
    REQUIRED_FIELDS = ['username']  

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    announcement=models.BooleanField(default=False)
    def __str__(self):
        return self.name

from django.core.validators import MinValueValidator
class Item(models.Model):
    categories = models.ManyToManyField(Category, related_name='items')
    users = models.ManyToManyField(CustomUser, related_name='items', blank=True)
    availablequantity=models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    weight=models.TextField(max_length=10, default='')
    description=models.TextField(max_length=500)
    price=models.FloatField(default=0)
    def __str__(self):
        return self.name

class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/', max_length=300)

class Expiry(models.Model):
    item = models.ForeignKey(Item, related_name='expiry', on_delete=models.CASCADE)
    date=models.DateTimeField()
    quantity=models.IntegerField()
    def __str__(self):
        return f'{self.date} - {self.item.name} - {self.quantity}'

class UserItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f'{self.user.username} - {self.item.name} - {self.quantity}'

class userhistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='history')
    name = models.CharField(max_length=100)
    quantity=models.IntegerField()
    totalprice=models.FloatField(default=0)
    datevar=models.CharField(max_length=100, default=str(datetime.now()))
