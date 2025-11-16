from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
import random

from orders.models import Company, Product, Order  

fake = Faker()

class Command(BaseCommand):
    help = "generate dummy data"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        self.stdout.write("creating ompanies...")
        companies = []
        for i in range(3): 
            c = Company.objects.create(name=f"Company {i+1}")
            companies.append(c)


        self.stdout.write("creating users...")

        roles_distribution = (
            ('viewer', 4),
            ('operator', 4),
            ('admin', 2),
        )

        users = []
        for role, count in roles_distribution:
            for i in range(count):
                u = User.objects.create_user(
                    username=f"{role}{i+1}",
                    password="1",
                    role=role,
                    is_superuser=True , # to make all users superusers for simplicity testing
                    is_staff=True,
                    company=random.choice(companies)
                )
                users.append(u)

        self.stdout.write("creating products...")
        products = []
        for company in companies:
            for i in range(7):  
                p = Product.objects.create(
                    company=company,
                    name=f"{company.name} Product {i+1}",
                    price=random.uniform(10, 500),
                    stock=random.randint(5, 200),
                    created_by=random.choice(users)
                )
                products.append(p)


        self.stdout.write("creating orders...")

        status_choices = ['pending', 'success', 'failed']

        all_orders = []
        for i in range(40): 
            product = random.choice(products)
            company = product.company

            quantity = random.randint(1, 10)

            if quantity > product.stock:
                status = random.choice(['pending', 'failed'])
            else:
                status = random.choice(status_choices)

            order = Order.objects.create(
                company=company,
                product=product,
                quantity=quantity,
                status=status,
                created_by=random.choice(users)
            )

            if order.status == 'success':
                order.shipped_at = timezone.now()

            order.save()

            all_orders.append(order)

        self.stdout.write(self.style.SUCCESS("data generated successfully"))
