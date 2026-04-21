# Book Metadata and Review Analytics API

A data-driven RESTful API built with **Django** and **Django REST Framework** for managing and analysing book metadata. The system supports full CRUD operations, flexible querying, analytical endpoints, JWT-based authentication, and an ownership-controlled review system.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Data Source](#data-source)
- [Data Models](#data-models)
- [Available Endpoints](#available-endpoints)
- [Query Parameters](#query-parameters)
- [Authentication](#authentication)
- [How to Run](#how-to-run)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Technical Report](#technical-report)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Generative AI Usage](#generative-ai-usage)

---

## Project Overview

This project implements a REST-style API for managing book metadata and user-generated reviews. It is backed by a cleaned public books dataset of 100 records spanning seven categories, and extends beyond basic CRUD functionality to include filtering, ordering, pagination, aggregation analytics, and JWT-authenticated review management with ownership-based permission control.

---

## Features

### Book Management
- Create, retrieve, update, and delete book records
- Retrieve a full paginated list or a single book by ID

### Query Features
- Filter by `title`, `author`, `year`, or `category`
- Order by `title` or `published_year` (ascending or descending)
- Paginate results using `page` and `page_size`

### Analytical Endpoints
- Overall dataset statistics (total books, year range, unique categories)
- 10 most recently published books
- Book count grouped by category
- Top-rated books ranked by average review score

### Authentication
- User registration
- JWT login and token refresh
- Protected endpoints using `Authorization: Bearer <access_token>`

### Review System
- Create, retrieve, update, and delete reviews
- Filter reviews by book ID
- Ownership enforcement: only the review author may update or delete their review

---

## Technology Stack

| Component            | Technology                      |
| -------------------- | ------------------------------- |
| Programming Language | Python                          |
| Web Framework        | Django                          |
| API Framework        | Django REST Framework           |
| Authentication       | SimpleJWT                       |
| Database             | SQLite                          |
| Data Preparation     | pandas                          |
| Testing              | Django TestCase + DRF APIClient |

---

## Project Structure

```
django_coursework/
├── bookproject/
│   ├── bookproject/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── pages/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── docs/
│   │   ├── api_documentation.pdf
│   │   └── technical_report.pdf
├── books_sample.csv
├── db.sqlite3
├── import_book.py
├── manage.py
├── README.md
└── requirements.txt
```

---

## Data Source

The project uses a publicly available books dataset. The raw dataset was cleaned using a standalone preparation script (`prepare_books_dataset.py`) before import. Preparation steps included:

- Selecting relevant columns (`title`, `author`, `year`, `category`, `description`)
- Removing image-related and unused fields
- Renaming columns to match the Django model schema
- Converting publication years to numeric form and removing invalid values
- Trimming whitespace and removing blank titles
- Deduplicating on `(title, author, year)`
- Sampling a subset of 100 records for coursework use

The cleaned subset is stored in `books_sample.csv` and imported via `import_book.py`.

---

## Data Models

### Book

| Field            | Type         | Notes                            |
| ---------------- | ------------ | -------------------------------- |
| `id`             | Integer      | Auto-generated primary key       |
| `title`          | CharField    | Required                         |
| `author`         | CharField    | Required                         |
| `published_year` | IntegerField | Validated during import          |
| `category`       | CharField    | Used for filtering and analytics |
| `description`    | TextField    | Optional                         |

A composite uniqueness constraint is applied on `(title, author, published_year)` to prevent duplicate imports.

### Review

| Field        | Type              | Notes                          |
| ------------ | ----------------- | ------------------------------ |
| `id`         | Integer           | Auto-generated primary key     |
| `book`       | ForeignKey → Book | Cascades on delete             |
| `user`       | ForeignKey → User | Links review to its author     |
| `rating`     | IntegerField      | Used for top-rated aggregation |
| `comment`    | TextField         | Optional                       |
| `created_at` | DateTimeField     | Auto-set on creation           |

### User

Django's built-in `User` model is used for registration, login, and review ownership. No custom profile extension is implemented in this version.

---

## Available Endpoints

### API Home
| Method | Endpoint | Description                        |
| ------ | -------- | ---------------------------------- |
| GET    | `/`      | Service overview and endpoint list |

### Authentication
| Method | Endpoint          | Description                   |
| ------ | ----------------- | ----------------------------- |
| POST   | `/register/`      | Create a new user account     |
| POST   | `/login/`         | Log in and receive JWT tokens |
| POST   | `/token/refresh/` | Issue a new access token      |

### Books
| Method | Endpoint       | Description                     |
| ------ | -------------- | ------------------------------- |
| GET    | `/books/`      | Paginated, filterable book list |
| POST   | `/books/`      | Create a new book record        |
| GET    | `/books/<id>/` | Retrieve a single book by ID    |
| PUT    | `/books/<id>/` | Update an existing book record  |
| DELETE | `/books/<id>/` | Delete a book record            |

### Book Analytics
| Method | Endpoint             | Description                             |
| ------ | -------------------- | --------------------------------------- |
| GET    | `/books/stats/`      | Total books, year range, category count |
| GET    | `/books/recent/`     | 10 most recently published books        |
| GET    | `/books/categories/` | Book count per category                 |
| GET    | `/books/top-rated/`  | Books ranked by average review rating   |

### Reviews
| Method | Endpoint         | Auth Required | Notes                        |
| ------ | ---------------- | ------------- | ---------------------------- |
| GET    | `/reviews/`      | No            | Supports `?book=<id>` filter |
| POST   | `/reviews/`      | Yes           | Creates a review             |
| GET    | `/reviews/<id>/` | No            | Retrieves a single review    |
| PUT    | `/reviews/<id>/` | Yes + Owner   | Updates own review only      |
| DELETE | `/reviews/<id>/` | Yes + Owner   | Deletes own review only      |

---

## Query Parameters

All parameters for `GET /books/` are optional and combinable.

| Parameter   | Description                              | Example                     |
| ----------- | ---------------------------------------- | --------------------------- |
| `title`     | Filter by title (substring match)        | `?title=Python`             |
| `author`    | Filter by author (substring match)       | `?author=Hawking`           |
| `year`      | Filter by exact publication year         | `?year=2017`                |
| `category`  | Filter by category (substring match)     | `?category=Computing`       |
| `ordering`  | Sort results                             | `?ordering=-published_year` |
| `page`      | Page number (default: 1)                 | `?page=2`                   |
| `page_size` | Records per page (default: 20, max: 100) | `?page_size=10`             |

**Supported ordering values:** `title`, `-title`, `published_year`, `-published_year`

**Example combined request:**

`GET /books/?category=Computing&ordering=-published_year&page=1&page_size=5`

---

## Authentication

Protected endpoints require a valid JWT access token in the request header:`Authorization: Bearer <access_token>`

### Register

POST /register/

```json
{
  "username": "testuser",
  "password": "test12345",
  "email": "test@example.com"
}
```

### Login

POST /login/

```json
{
  "username": "testuser",
  "password": "test12345"
}
```

A successful login returns both an `access` token and a `refresh` token. Use the `access` token in the `Authorization` header for all protected requests.

---

## How to Run

### 1. Clone the Repository

```bash
git clone git@github.com:EEEVA0/201691049_Zhang-Xiyan.git
cd 201691049_Zhang-Xiyan
```

Run all commands from the project root directory, where `manage.py` and `requirements.txt` are located.

### 2. Create and Activate a Virtual Environment

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Import the Dataset

```bash
python import_book.py
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

### 7. Access the API

| URL                            | Description       |
| ------------------------------ | ----------------- |
| `http://127.0.0.1:8000/`       | API home          |
| `http://127.0.0.1:8000/books/` | Books endpoint    |
| `http://127.0.0.1:8000/admin/` | Django admin site |

---

## Testing

Run all automated tests with:

```bash
python manage.py test
```

The test suite covers:

- API home endpoint
- Book list retrieval and single book retrieval
- Book creation and 404 handling for invalid IDs
- Filtering by title, author, year, and category
- Ordering by title and publication year
- Pagination behaviour
- All four analytical endpoints

JWT authentication and review ownership rules were additionally verified through manual testing using authenticated HTTP requests.

---

## API Documentation

The full API documentation is available in the `docs/` folder:

- [API Documentation (PDF)](docs/api_documentation.pdf)

---

## Technical Report

The technical report covering design choices, technology justification, challenges, testing approach, limitations, and Generative AI usage is available in the `docs/` folder:

- [Technical Report (PDF)](docs/technical_report.pdf)

---

## Limitations

- Django's default `User` model is used without profile extensions
- The dataset is a cleaned and reduced subset of the original source
- Search relies on simple substring filtering rather than full-text search
- One review per user per book is not currently enforced at the model level
- The project is designed for local execution; external deployment has not been completed in this version

---

## Future Improvements

- External deployment to a hosting platform such as Railway or Render
- Richer user profiles with extended fields
- Recommendation logic based on review history and category preferences
- Full-text search using PostgreSQL's native capabilities or an external engine
- Role-based access control for admin and moderator roles
- Class-based views or ViewSets for cleaner endpoint organisation
- Automatic OpenAPI / Swagger documentation via `drf-spectacular`
- Broader automated test coverage for authentication and permission edge cases

---

## Generative AI Usage

Generative AI tools were used throughout this project to support:

- Project planning and API scope definition
- Understanding Django REST Framework concepts such as serialisers and queryset annotations
- Dataset cleaning logic and import script development
- Debugging implementation issues including JWT token handling
- Drafting and refining the API documentation and technical report
- Reflecting on design alternatives and architectural trade-offs

All AI-generated outputs were reviewed, tested, and manually revised before inclusion in the final project. AI tools were used as a development and writing aid, not as a replacement for genuine understanding or decision-making.