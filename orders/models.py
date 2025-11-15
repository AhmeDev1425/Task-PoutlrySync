from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import logging

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('operator', 'Operator'),
        ('viewer', 'Viewer'),
    )

    role = models.CharField(max_length=10, choices=ROLES, default='viewer')
    company = models.ForeignKey('Company', on_delete=models.PROTECT, null=True, blank=True, related_name='users')

class AbstractCreationInfo(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        editable=False,
        related_name="%(class)s_created",  # allows reverse lookup
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True

class Company(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name

class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Product(AbstractCreationInfo):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255,unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    last_updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


    objects = models.Manager() # includes soft-deleted items
    active_objects = ProductManager()

    class Meta:
        unique_together = ('company', 'name')

    @classmethod
    def purchase_product(cls, product_id, quantity):
        with transaction.atomic():
            product = cls.objects.select_for_update().get(id=product_id)        
            product.stock -= quantity
            product.save()
            return product

    def __str__(self):
        return self.name

class Order(AbstractCreationInfo):
    STATUS_CHOICES = (('pending','pending'),('success','success'),('failed','failed'))
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    shipped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['company', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  #does instance new
        prev_status = None

        if not is_new:
            prev_status = Order.objects.values_list('status', flat=True).get(pk=self.pk)

        super().save(*args, **kwargs)

        if self.status == 'success' and (is_new or prev_status != 'success'):
            if not self.shipped_at:
                self.shipped_at = timezone.now()
                super().save(update_fields=['shipped_at'])

            logger = logging.getLogger('orders.confirmation')
            logger.info(
                "Order %s for company %s by %s marked SUCCESS. product=%s qty=%s shipped_at=%s",
                self.pk, self.company_id, self.created_by_id, self.product_id, self.quantity, self.shipped_at
            )
