from django.db import models
from djmoney.models.fields import MoneyField
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File
import random
from django.contrib.auth.models import User

# Create your models here.

def generate_barcode():
    length = 11
    new = ['0','1','2','3','4','5','6','7','8','9']
    code = ''.join(random.choices(new, k=length))
    full_code = f"MP{code}"
    return full_code

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
    weight = models.IntegerField()
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    barcode = models.CharField(max_length=200, unique=True, default=generate_barcode)
    in_manifest = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner.username} {self.id} {self.sender_name} {self.sender_surname} \
        {self.receiver_city} {self.weight} {self.in_manifest} \
        {self.price} {self.barcode}'

    class Meta:
        ordering = ('-created_at',)

    def generate_barcode_image(self):
        code_39 = barcode.get_barcode_class('code39')
        ean = code_39(f'{self.barcode}', writer=ImageWriter())
        buffer = BytesIO()
        result = ean.write(buffer)
        return result

