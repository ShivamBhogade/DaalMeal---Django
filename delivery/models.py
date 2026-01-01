from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=150)

    def __str__(self):
        return self.username
    
class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    cuisine_type = models.CharField(max_length=100)
    picture_url = models.URLField(blank=True, null=True, default='https://www.cntraveller.in/story/6-new-restaurants-to-try-in-bengaluru/')
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name    

class MenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="menu_items"
    )
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

class Order(models.Model):
    STATUS_CHOICES = [
        ("PLACED", "Placed"),
        ("PREPARING", "Preparing"),
        ("OUT_FOR_DELIVERY", "Out for Delivery"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PLACED"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.menu_item.name
