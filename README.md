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
javarush_django_project/
├── config/                     # Django project configuration
│   ├── __init__.py
│   ├── settings.py             # Main settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI application
│   └── asgi.py                 # ASGI application
│
├── products/                   # Product catalog app
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                # Admin customization
│   ├── apps.py
│   ├── models.py               # Category, Product models
│   ├── views.py                # HomeView, ProductListView, ProductDetailView, ProductViewSet
│   ├── serializers.py          # ProductSerializer, ReviewSerializer
│   ├── urls.py                 # Product URLs
│   └── tests.py
│
├── orders/                     # Order and cart management
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                # Order admin with analytics
│   ├── apps.py
│   ├── models.py               # Order, OrderItem models
│   ├── cart.py                 # Session-based cart class
│   ├── context_processor.py   # Cart context for templates
│   ├── views.py                # Cart, Checkout, OrderViewSet
│   ├── serializers.py          # OrderSerializer, CartAPIView
│   ├── services.py             # Email notification services
│   ├── forms.py                # Checkout form
│   ├── urls.py                 # Order URLs
│   └── tests.py
│
├── users/                      # User authentication and profiles
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Custom User model
│   ├── views.py                # RegisterView, ProfileView, PasswordChangeView
│   ├── serializers.py          # UserSerializer, UserRegistrationSerializer
│   ├── forms.py                # RegisterForm, ProfileUpdateForm
│   ├── urls.py                 # User URLs
│   └── tests.py
│
├── reviews/                    # Product reviews
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Review model
│   ├── views.py                # ReviewCreateView
│   ├── forms.py                # ReviewForm
│   ├── urls.py                 # Review URLs
│   └── tests.py
│
├── templates/                  # HTML templates
├── static/                     # Static files
│   ├── css/
│   │   └── main.css            # Main stylesheet
│   ├── js/
│   │   ├── main.js             # Main JavaScript
│   │   └── cart.js             # Cart functionality
│   └── img/                    # Images
│       ├── products/           # Product images
│       ├── background/         # Background images
│       ├── icons/              # UI icons
│       └── avatars/            # User avatars
│
├── manage.py                   # Django management script
├── pyproject.toml              # UV project configuration
├── uv.lock                     # UV lock file
├── setup.cfg                   # Linting configuration
├── pyrightconfig.json          # Type checking configuration
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
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