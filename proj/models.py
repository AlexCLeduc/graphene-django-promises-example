from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="products"
    )

    def __str__(self):
        return f"{self.name} - {self.price}"


class Order(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="orders")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.date}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.order} - {self.product} - {self.quantity}"


class Delivery(models.Model):
    order = models.OneToOneField(
        "Order", on_delete=models.CASCADE, related_name="delivery"
    )
    address = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.order} - {self.address}"


class DeliveryLineItem(models.Model):
    delivery = models.ForeignKey(
        "Delivery", on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="delivery_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.delivery} - {self.product} - {self.quantity}"
