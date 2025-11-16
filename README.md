# Multi-Tenant Ordering System

A Django-based multi-tenant ordering platform where each company manages its own products and orders.  
The system enforces data isolation, role-based permissions, soft deletion, CSV export, and includes full Dockerization using MySQL and Gunicorn.

---

## Table of Contents
1. Introduction  
2. Features  
3. Tech Stack  
4. System Architecture  
5. Multi-Tenancy Model  
6. Data Models  
7. API Endpoints  
8. Access Control Rules  
9. Email Logging  
10. Admin Features  
11. Demo Data  
12. Project Structure  
13. Local Setup (non-Docker)  
14. Docker Setup & Deployment  
15. Running Migrations  
16. Useful Commands  
17. Notes  

---

## 1. Introduction
This project implements a multi-tenant ordering system in Django where each authenticated user belongs to one company.  
Tenants (companies) are logically isolated, ensuring that products and orders of each company remain private to that company.

The API exposes CRUD operations for managing products and orders and supports CSV export and soft deletion.  
A simple HTML interface is included at the index page.

---

## 2. Features
- Multi-tenant data isolation (per company)
- Role-based permissions:
  - Admin: full access
  - Operator: limited order editing
  - Viewer: read-only
- Product management with soft deletion
- Order creation with stock checks
- CSV export of orders
- Logging confirmation emails upon successful orders
- Full REST API with Swagger and Redoc documentation
- Django admin customization with export/bulk-actions
- Fully dockerized environment with MySQL & Gunicorn
- Simple HTML interface for product listing and creation

---

## 3. Tech Stack
- Python 3.10+
- Django 5.x
- Django REST Framework
- MySQL 5.7
- Gunicorn
- drf-yasg (Swagger / Redoc)
- Docker & Docker Compose

---

## 4. System Architecture
The system consists of:
- A Django web application (REST API + Admin + HTML)
- A MySQL database
- Gunicorn application server
- Optional static serving via Django in development

---

## 5. Multi-Tenancy Model
This project uses **shared-database, shared-schema multi-tenancy**.

Tenant isolation is enforced through:
- Each user belonging to exactly one company
- All Product and Order objects having a company foreign key
- QuerySets automatically filtering data by the authenticated user’s company

No row belonging to another company is visible or accessible.

---

## 6. Data Models

### Company
- name

### User (extended model)
- company (one-to-many)
- role: `admin` | `operator` | `viewer`
  
u can try users 
username:
    admin1 or operator1 or viewer1 
password: 
    1

### Product
- company  
- name  
- price  
- stock  
- created_by  
- created_at (immutable)  
- last_updated_at  
- is_active (soft delete flag)

### Order
- company  
- product  
- quantity  
- created_by  
- created_at (immutable)  
- status: pending | success | failed  
- shipped_at (set automatically when status = success)

---

## 7. API Endpoints

### Products
```
GET    /api/products/       → List active products for the authenticated user's company
DELETE /api/products/       → Soft delete one or more products (admin only)
```

### Orders
```
POST   /api/orders/           → Create orders (one or more)
PATCH  /api/orders/<id>/      → Update order (restricted for operator)
PUT    /api/orders/<id>/      → Replace order
GET    /api/orders/export/    → Export orders as CSV
```

### Documentation
```
/swagger/   → Swagger UI  
/redoc/     → Redoc UI
```

### Index Page
```
/     → Simple HTML page with product form + table
```

---

## 8. Access Control Rules

1. Data access is always limited to the user's company.
2. Viewer users:
   - Cannot place orders.
3. Operator users:
   - Can only modify orders created today.
4. Admin users:
   - Full access.
5. Orders cannot include inactive products.
6. Orders cannot be created when requested quantity exceeds stock.

---

## 9. Email Logging
When an order is marked as **success**, a simulated confirmation email is logged to:

```
order_confirmations.log
```

The log includes:
- Order ID  
- Company  
- User  
- Timestamp  
- Product details  

Log rotation is handled automatically.

---

## 10. Admin Features

### Products Admin
- Bulk action to mark selected products as inactive

### Orders Admin
- Action to export selected orders as CSV

---

## 11. Demo Data
The project includes demo data using Faker.  
It generates:
- Companies  
- Users (admin / operator / viewer)  
- Products  
- Orders  

This allows testing API behavior easily.

---

## 12. Project Structure
A simplified structure:

```
project/
    settings.py
    urls.py

orders/
    models.py
    views.py
    serializers.py
    admin.py
    urls.py
    DTL/index.html

Dockerfile
docker-compose.yml
requirements.txt
README.md
```

---

## 13. Local Setup (without Docker)

### Create virtual environment
```
python -m venv venv
source venv/bin/activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### Run migrations
```
python manage.py migrate
```

### Start development server
```
python manage.py runserver
```

### Make dummy data 
```
python manage.py seed_data
```
it will make some compaies and diffrent users roles and products for companies
---

## 14. Docker Setup & Deployment

### Build and run containers
```
docker-compose up --build
```
or for new versions
```
docker compose up --build
```

### Start without rebuild
```
docker compose up
```

The application will be available at:
```
http://0.0.0.0:8000
```

The MySQL server runs on:
```
localhost:3306
```

### Environment Variables
Django reads DB settings from variables defined in `docker-compose.yml`:

```
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

---

## 15. Running Migrations inside Docker

### Enter the Django container
```
docker exec -it django_app bash
```

### Apply migrations
```
python manage.py migrate
```

### Create superuser
```
python manage.py createsuperuser
```

---

## 16. Useful Commands

### Rebuild from scratch
```
docker-compose down -v
docker-compose up --build
```

### Open bash inside Django container
```
docker exec -it django_app bash
```

### Open MySQL shell
```
docker exec -it mysql_db mysql -u root -p
```

---

## 17. Notes
- All services bind to `0.0.0.0`
- Data isolation is strictly enforced in all queries
- Stock validation prevents invalid orders
- Nginx can be added later for production deployment
- Swagger and Redoc are enabled for API documentation

---

End of README.
