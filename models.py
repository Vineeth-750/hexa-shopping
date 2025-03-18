from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


# Create your models here.

class Category(models.TextChoices):
    NONE = '', 'None'
    MEN = 'Men', 'Men'
    WOMEN = 'Women', 'Women'
    KIDS = 'Kids', 'Kids'
    ACCESSORIES = 'Accessories', 'Accessories'


class Customer(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)  # Ensure unique emails
    number = models.CharField(max_length=20)  # Changed to CharField for phone numbers
    password = models.CharField(max_length=255)  # Store hashed password
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=10)  # CharField for postal codes

    def __str__(self):
        return f"{self.firstname}, {self.lastname}, {self.email}"


class Product(models.Model):
    productname = models.CharField(max_length=255)
    image = models.ImageField(upload_to='productimg/')
    price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True, default="")
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.NONE
    )
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.productname


from django.db import models

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Total cost for this product (price * quantity)
    date_added = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    total_products = models.IntegerField(default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Grand total for the order
    date_placed = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='Pending')

    def __str__(self):
        return f"Order({self.customer.name}, {self.total_products}, {self.grand_total})"
    

class Ordersub(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"




class Complaints(models.Model):
    complaint = models.TextField()  
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)  
    date = models.DateField(auto_now_add=True)  
    replied = models.BooleanField(default=False)

    def __str__(self):
        return f"Complaint by {self.customer} on {self.date}"

class Reply(models.Model):
    complaint = models.ForeignKey(Complaints, related_name="replies", on_delete=models.CASCADE)
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to complaint {self.complaint.id} on {self.created_at}"



