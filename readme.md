# Task API

A simple RESTful Task API built with **FastAPI**, **SQLite**, and
**Supabase Authentication**.

The project demonstrates: - REST API design with FastAPI - Request
validation with Pydantic - CRUD operations using SQLite - User signup
and login through Supabase Auth - Bearer-token authentication for
protected endpoints - Automatic interactive API documentation through
Swagger UI

## Tech Stack

-   **Python**
-   **FastAPI**
-   **Pydantic**
-   **SQLite**
-   **Supabase Auth**
-   **python-dotenv**
-   **Uvicorn**

## Project Structure

``` text
.
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── tasks.db              # Created automatically when the application starts
```

> `tasks.db` is generated locally by the application and should normally
> not be committed to GitHub.

## Prerequisites

Install:

-   Python 3.10+
-   pip
-   A Supabase project

## Installation

### 1. Clone the repository

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

### 2. Create a virtual environment

Linux/macOS:

``` bash
python -m venv venv
source venv/bin/activate
```

Windows:

``` powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

If `requirements.txt` has not been created yet, the required packages
are:

``` bash
pip install fastapi uvicorn pydantic supabase python-dotenv
```

## Environment Variables

Create a `.env` file in the project root:

``` env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_key
```

Replace the values with credentials from your own Supabase project.

### Security

**Never commit `.env` to GitHub.**

Your `.gitignore` should contain at least:

``` gitignore
.env
venv/
__pycache__/
*.pyc
tasks.db
```

Do not place Supabase credentials directly in the source code.

If a secret is accidentally committed, remove it from the repository and
rotate/revoke the exposed credential. Simply deleting the file in a
later commit does not make the secret safe.

## Running the API

Start the development server with:

``` bash
uvicorn main:app --reload
```

The API will normally be available at:

``` text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically provides interactive documentation.

### Swagger UI

Open:

``` text
http://127.0.0.1:8000/docs
```

### ReDoc

Open:

``` text
http://127.0.0.1:8000/redoc
```

## API Reference

  --------------------------------------------------------------------------------
  Method           Endpoint                         Auth Required Description
  ---------------- ------------------------ --------------------- ----------------
  GET              `/`                                         No Returns API
                                                                  information

  GET              `/health`                                   No Health check

  POST             `/auth/signup`                              No Creates a
                                                                  Supabase user

  POST             `/auth/login`                               No Authenticates a
                                                                  user and returns
                                                                  access/refresh
                                                                  tokens

  POST             `/auth/logout`                             Yes Signs out
                                                                  through Supabase

  GET              `/public/info`                              No Returns public
                                                                  information

  GET              `/protected/profile`                       Yes Returns the
                                                                  authenticated
                                                                  user's profile

  GET              `/protected/dashboard`                     Yes Returns a
                                                                  protected
                                                                  dashboard
                                                                  response

  GET              `/tasks`                                    No Returns all
                                                                  tasks

  GET              `/task/{task_id}`                           No Returns a task
                                                                  by ID

  POST             `/tasks`                                    No Creates a task

  PUT              `/tasks/{id}`                               No Updates a task

  DELETE           `/tasks/{id}`                               No Deletes a task
  --------------------------------------------------------------------------------

> **Authentication note:** In the current implementation, only the
> endpoints under `/protected/*` and `/auth/logout` require a Bearer
> token. The task CRUD endpoints are currently public.

## Authentication Flow

### 1. Sign up

Send:

``` http
POST /auth/signup
Content-Type: application/json
```

Request body:

``` json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

### 2. Log in

Send:

``` http
POST /auth/login
Content-Type: application/json
```

Request body:

``` json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

A successful login returns:

``` json
{
  "access_token": "your-access-token",
  "refresh_token": "your-refresh-token"
}
```

### 3. Access a protected endpoint

Include the access token as a Bearer token:

``` http
Authorization: Bearer your-access-token
```

For example:

``` http
GET /protected/profile
Authorization: Bearer your-access-token
```

The API verifies the token using Supabase Auth.

## Task Examples

### Create a task

``` http
POST /tasks
Content-Type: application/json
```

``` json
{
  "title": "Learn FastAPI",
  "done": false
}
```

### Update a task

``` http
PUT /tasks/1
Content-Type: application/json
```

``` json
{
  "title": "Learn FastAPI",
  "done": true
}
```

### Get all tasks

``` http
GET /tasks
```

Example response:

``` json
[
  {
    "id": 1,
    "title": "Learn Python",
    "done": false
  },
  {
    "id": 2,
    "title": "Build a SQLite database",
    "done": false
  }
]
```

### Get a task by ID

``` http
GET /task/1
```

### Delete a task

``` http
DELETE /tasks/1
```

## Swagger UI Screenshot

Add a screenshot of the running Swagger UI here after starting the
application.

Suggested filename:

``` text
docs/swagger-ui.png
```

Then add:

``` markdown
![Swagger UI](docs/swagger-ui.png)
```

Example section:

![Swagger UI](docs/swagger-ui.png)

## Database

The application uses SQLite for task storage.

On startup, the API creates `tasks.db` automatically if it does not
already exist.

The database contains:

``` text
tasks
├── id
├── title
└── done
```

The application also inserts three example tasks when the database is
empty.

## Error Handling

The API uses appropriate HTTP status codes for common errors, including:

-   `400 Bad Request` --- invalid request data
-   `401 Unauthorized` --- invalid or expired authentication token
-   `404 Not Found` --- requested task does not exist
-   `204 No Content` --- successful logout

FastAPI/Pydantic also validates request bodies automatically.

## Testing the API

After starting the server, open Swagger UI:

``` text
http://127.0.0.1:8000/docs
```

From there, the endpoints can be tested directly from the browser.

For protected endpoints:

1.  Create an account using `/auth/signup`.
2.  Log in using `/auth/login`.
3.  Copy the returned `access_token`.
4.  Use the **Authorize** button in Swagger UI.
5.  Enter the Bearer token.
6.  Call the protected endpoint.

## GitHub Checklist

Before publishing the repository:

-   [ ] `.env` is included in `.gitignore`
-   [ ] Supabase secrets are not present in source code
-   [ ] `tasks.db` is ignored
-   [ ] `venv/` is ignored
-   [ ] `requirements.txt` is included
-   [ ] README is included
-   [ ] Swagger UI screenshot is included
-   [ ] Repository can be cloned successfully
-   [ ] A new `.env` can be created with the user's own Supabase
    credentials
-   [ ] API starts with `uvicorn main:app --reload`
-   [ ] Swagger UI opens at `/docs`
-   [ ] Authentication works with the new Supabase project

## License

This project is available for educational and portfolio purposes.
