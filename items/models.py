from django.db import models
from django.db.models.deletion import CASCADE
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
import random
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()
# Create your models here.


def generate_barcode():
    length = 11
    new = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    code = ''.join(random.choices(new, k=length))
    full_code = f"MP{code}"
    return full_code


def generate_random_code():
    length = 8
    new = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    code = ''.join(random.choices(new, k=length))
    full_code = f"{code}"
    return full_code


class Manifest(models.Model):
    sender_city = models.CharField(max_length=255)
    receiver_city = models.CharField(max_length=255)
    manifest_code = models.CharField(
        max_length=8, unique=True, default=generate_random_code)
    cmr = models.CharField(max_length=10, unique=True)
    car_number = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.manifest_code}'

    class Meta:
        ordering = ('-created_at',)

    def total_item(self):
        pass


class Item(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=100)
    sender_surname = models.CharField(max_length=100)
    company = models.CharField(max_length=200, blank=True)
    sender_country = models.CharField(max_length=200)
    sender_city = models.CharField(max_length=200)
    receiver_name = models.CharField(max_length=100)
    receiver_surname = models.CharField(max_length=100)
    receiver_id = models.CharField(max_length=100, blank=True)
    receiver_country = models.CharField(max_length=200)
    receiver_city = models.CharField(max_length=200)
    receiver_address = models.CharField(max_length=200, blank=True)
    receiver_number = models.CharField(max_length=200, blank=True)
    description = models.TextField(max_length=500, blank=True)
    weight = models.FloatField(blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=20, default='USD')
    barcode = models.CharField(
        max_length=200, unique=True, default=generate_barcode)
    barcode_image = models.ImageField(upload_to='images/', blank=True)
    in_manifest = models.BooleanField(default=False, blank=True, null=True)
    arrived = models.BooleanField(default=False)
    manifest_number = models.ForeignKey(Manifest, on_delete=models.SET_NULL,
                                        related_name="item", null=True, default=None, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner.username} {self.id} \
        {self.sender_surname} {self.sender_name} {self.receiver_city} \
        {self.weight} {self.price} {self.barcode} {self.in_manifest} \
        {self.barcode_image}'

    class Meta:
        ordering = ('-created_at',)

    def get_barcode_image(self):
        if self.barcode_image:
            return 'http://127.0.0.1:8000' + self.barcode_image.url
        return None

    def save(self, *args, **kwargs):
        code_39 = barcode.get_barcode_class('code39')
        ean = code_39(f'{self.barcode}', writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode_image.save(
            f'{self.company}/{self.owner}/barcode.png', File(buffer), save=False)
        return super().save(*args, **kwargs)
