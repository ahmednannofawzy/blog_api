# Blog API

A robust, production-ready RESTful API for a Blogging platform built with **FastAPI**, **SQLAlchemy**, and **MySQL**, fully containerized using **Docker** and **Docker Compose**.

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** MySQL 8.0
- **ORM:** SQLAlchemy (PyMySQL Driver)
- **Authentication:** JWT (JSON Web Tokens) with Passlib & Bcrypt
- **Containerization:** Docker & Docker Compose
- **Validation:** Pydantic v2

---

## Features

- **User Authentication:** Registration, Login with JWT token generation, and secure password hashing.
- **Posts Management:** Full CRUD operations for blog posts (Create, Read, Update, Delete) linked to authenticated users.
- **Comments System:** Add and delete comments on specific posts with authorization checks.
- **Database Relationships:** Cascading deletes and ORM relationships between Users, Posts, and Comments.
- **Interactive Documentation:** Auto-generated Swagger UI and ReDoc interfaces.

---

## Getting Started (Docker Setup)

The easiest way to run the application is using Docker Compose.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.

### Installation & Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/blog_api.git](https://github.com/your-username/blog_api.git)
   cd blog_api
   ```
