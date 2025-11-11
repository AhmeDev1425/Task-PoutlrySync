from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    # admin | operator | viewer

    ROLES = (
        ('admin', 'Admin'),
        ('operator', 'Operator'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='viewer')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True)


class AbstractCreationInfo(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",  # allows reverse lookup
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Company(models.Model):
    name = models.CharField(max_length=255,unique=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)


class Product(AbstractCreationInfo):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255,unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    last_updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    objects = ProductManager()
    all_objects = models.Manager()  # includes soft-deleted items

    def purchase_done(self):
        if self.stock > 0 :
            self.stock -= 1
            self.last_updated_at = timezone.now()
            self.save()

class Order(AbstractCreationInfo):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50)
    shipped_at = models.DateTimeField(null=True, blank=True)