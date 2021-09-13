from django.db import models
from djongo.models.fields import ObjectIdField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import random


class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ips = models.Field(default=[])
    subprofiles = models.Field(default={})
    btc_wallet = models.FloatField(default=random.randint(1, 10))
    btc_original = models.FloatField(default=0)
    cash_wallet = models.FloatField(default=100000)

    def __str__(self):
        return f"{self.user}({self._id})"


class Order(models.Model):
    order_type = (
        ('BUY', 'BUY'),
        ('SELL', 'SELL')
    )

    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    type = models.Field(max_length=50, choices=order_type, default='')
    quantity = models.FloatField(validators=[MinValueValidator(1)])
    price = models.FloatField(validators=[MinValueValidator(1)])
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Order {self.pk} : {self.quantity} BTC - {self.price}$ - {self.type} by {self.user}" \
               f" active {self.active})"

    def media_pric(self):
        order_b = Order.objects.filter(type='BUY').filter(active=True)
        order_s = Order.objects.filter(type='SELL').filter(active=True)
        price_b = 0
        price_s = 0
        count_b = 0
        count_s = 0
        if len(order_b) > 0:
            for order in order_b:
                price_b += order.price
                count_b += 1
            price_b /= count_b
        if len(order_s) > 0:
            for order in order_s:
                price_s += order.price
                count_s += 1
            price_s /= count_s
        return price_b, price_s

