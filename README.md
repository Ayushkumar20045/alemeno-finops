# Alemeno FinOps Backend

A FastAPI-based transaction processing system that ingests CSV files, processes transactions asynchronously using Celery, stores results in a database, detects anomalies, and provides REST APIs for querying job status and transaction data.

## Features

- CSV upload and processing
- Asynchronous task execution with Celery
- Transaction storage using SQLAlchemy
- Job tracking and status APIs
- Summary generation
- Transaction filtering
- Anomaly detection
- Docker support

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Celery
- Docker
- SQLite
- Pydantic

## Project Structure

```text
app/
├── api/
├── database/
├── models/
├── services/
├── tasks/
main.py
Dockerfile
docker-compose.yml
requirements.txt
```

## API Endpoints

### Upload CSV

```http
POST /jobs/upload
```

Uploads a CSV file and starts background processing.

### Get All Jobs

```http
GET /jobs
```

Returns all processing jobs.

### Get Job Status

```http
GET /jobs/{job_id}/status
```

Returns the status and summary of a job.

### Get Job Results

```http
GET /jobs/{job_id}/results
```

Returns:

- Cleaned transactions
- Flagged anomalies
- Category breakdown
- Summary

### Get Transactions

```http
GET /transactions
```

Supports:

- Category filtering
- Status filtering
- Pagination

Example:

```http
GET /transactions?category=Food&status=SUCCESS
```

## Running Locally

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start FastAPI

```bash
uvicorn main:app --reload
```

### Start Celery Worker

```bash
celery -A app.celery_app worker --loglevel=info
```

## Docker

Build:

```bash
docker-compose build
```

Run:

```bash
docker-compose up
```

## Author

Ayush Kumar

GitHub:
https://github.com/Ayushkumar20045