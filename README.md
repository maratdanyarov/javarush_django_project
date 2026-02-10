# Hop & Barley - Django E-Commerce Store

A full-featured e-commerce application built with Django and Django REST Framework. This project transforms a static HTML/CSS beer brewing supplies shop template into a fully functional online store with web interface, REST API, and admin panel.

## Features

- **Product Catalog**: Browse products with filtering, sorting, search, and pagination
- **Shopping Cart**: Session-based cart with AJAX updates and stock validation
- **Order Management**: Checkout with email notifications
- **User Accounts**: Registration, profile management, order history
- **Reviews**: Product reviews with ratings (only for purchased products)
- **REST API**: Complete API with JWT authentication
- **Admin Analytics**: Dashboard with revenue, top products, and order statistics
- **API Documentation**: Swagger/OpenAPI documentation

## Tech Stack

- **Backend**: Django 6.0.1, Django REST Framework 3.16
- **Database**: PostgreSQL 15
- **Authentication**: Session-based (web) + JWT (API)
- **API Docs**: drf-spectacular (Swagger/OpenAPI)
- **Package Manager**: UV
- **Containerization**: Docker & Docker Compose

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/maratdanyarov/javarush_django_project.git
cd javarush_django_project

# Start services
docker-compose up --build

# In another terminal, create a superuser
docker-compose exec web uv run python manage.py createsuperuser
```

The application will be available at:
- **Web**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/

### Local Development

```bash
# Install dependencies
uv sync

# Set up environment variables
export DEBUG=True
export DB_HOST=localhost

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Start development server
uv run python manage.py runserver
```

## Project Structure

```
/
├── config/                 # Django settings and URL configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/               # Product catalog app
│   ├── models.py           # Category, Product
│   ├── views.py            # List, Detail views + API ViewSet
│   └── serializers.py
├── orders/                 # Orders and cart management
│   ├── models.py           # Order, OrderItem
│   ├── cart.py             # Session-based cart
│   ├── views.py            # Cart, Checkout views + API
│   └── services.py         # Email notifications
├── users/                  # User authentication and profiles
│   ├── models.py           # Custom User model
│   ├── views.py            # Register, Profile views + API
│   └── forms.py
├── reviews/                # Product reviews
│   ├── models.py           # Review model
│   └── views.py            # Review creation
├── templates/              # Django HTML templates
├── static/                 # CSS, JavaScript, images
├── tests/                  # Test files
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## API Endpoints

### Authentication
| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/token/` | POST | Obtain JWT tokens | No |
| `/api/token/refresh/` | POST | Refresh access token | No |
| `/api/users/register/` | POST | User registration | No |
| `/api/users/profile/` | GET, PUT | User profile | JWT |

### Products
| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/products/` | GET | List products (filterable, searchable) | No |
| `/api/products/{id}/` | GET | Product detail | No |
| `/api/products/{id}/reviews/` | GET, POST | Product reviews | GET: No, POST: JWT |

### Orders
| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/orders/` | GET, POST | List/create orders | JWT |
| `/api/orders/{id}/` | GET, PATCH | Order detail/update | JWT |

### Cart
| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/cart/` | GET | View cart | No |
| `/api/cart/` | POST | Add to cart | No |
| `/api/cart/` | PATCH | Update quantity | No |
| `/api/cart/` | DELETE | Remove/clear cart | No |

### API Documentation
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## JWT Authentication Example

```bash
# Get tokens
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "youruser", "password": "yourpass"}'

# Use access token
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer <access_token>"

# Refresh token
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

## Running Tests

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific app tests
uv run pytest products/tests.py -v
```

## Linting

```bash
# Install dev dependencies
uv sync --extra dev

# Run flake8
uv run flake8

# Run mypy (type checking)
uv run mypy .
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret key | (insecure default) |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | Database name | `postgres` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `db` |
| `DB_PORT` | Database port | `5432` |
| `EMAIL_BACKEND` | Email backend | Console backend |
| `EMAIL_HOST` | SMTP host | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |

## Implementation Checklist

- [x] Docker Compose setup with PostgreSQL
- [x] Product catalog with filtering, search, pagination
- [x] Product sorting (price, popularity, newness)
- [x] Product detail page with reviews
- [x] Shopping cart (session-based, AJAX)
- [x] Order checkout with validation
- [x] Email notifications on order
- [x] User registration and authentication
- [x] User profile and password change
- [x] Order history
- [x] Admin panel with analytics
- [x] REST API with JWT authentication
- [x] API documentation (Swagger/OpenAPI)
- [x] Tests (pytest-django)
- [x] Linting configuration (flake8, mypy)

## Admin Features

- **Order Analytics**: `/admin/orders/order/analytics/`
  - Total revenue
  - Order count by status
  - Top 10 selling products
  - Recent orders
- **Custom Actions**:
  - Mark orders as paid/shipped/delivered/cancelled
  - Activate/deactivate products

## License

This project is for educational purposes.