# Alemeno FinOps Backend

A FastAPI-based transaction processing system that ingests CSV files, processes transactions asynchronously using Celery and Redis, stores data in PostgreSQL, detects anomalies, and generates AI-powered insights using Google Gemini.

---

## Features

- CSV upload and processing
- Asynchronous task execution using Celery
- Redis message broker
- PostgreSQL database storage
- Duplicate transaction removal
- Data normalization and cleaning
- Transaction anomaly detection
- Summary statistics generation
- Category-wise spending breakdown
- Retry failed jobs
- AI-powered narrative insights using Gemini 2.5 Flash
- REST APIs for querying jobs and transactions
- Dockerized deployment

---

## Tech Stack

### Backend
- FastAPI
- Python
- SQLAlchemy

### Database
- PostgreSQL

### Asynchronous Processing
- Celery
- Redis

### AI Layer
- Google Gemini 2.5 Flash

### Containerization
- Docker
- Docker Compose

---

## Project Structure

```text
alemeno-finops/
│
├── app/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── tasks/
│   └── celery_app.py
│
├── uploads/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
└── README.md
```
## High-Level Architecture

![Architecture Diagram](docs/architecture.png)

---

## API Endpoints

### Upload CSV

```http
POST /jobs/upload
```

Uploads a transaction CSV file and starts asynchronous processing.

---

### Get All Jobs

```http
GET /jobs
```

Returns all jobs and their status.

---

### Get Job Status

```http
GET /jobs/{job_id}/status
```

Returns:

- Processing status
- Summary statistics

---

### Get Job Results

```http
GET /jobs/{job_id}/results
```

Returns:

- Cleaned transactions
- Flagged anomalies
- Category breakdown
- Summary statistics

---

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

---

### Retry Failed Job

```http
POST /jobs/{job_id}/retry
```

Retries a failed processing job.

---

### Get AI Insights

```http
GET /jobs/{job_id}/insights
```

Returns:

- Total INR spend
- Total USD spend
- Top merchants
- Anomaly count
- Narrative summary
- Risk level

---

## Anomaly Detection Rules

### High Amount Transactions

Transactions are flagged if:

```text
Amount > 3 × account median
```

### Currency Mismatch

Transactions are flagged when domestic merchants use USD currency.

Examples:

- Swiggy + USD
- Ola + USD
- IRCTC + USD

---

## AI-Powered Insights

Powered by Google Gemini 2.5 Flash.

Generates:

- Spending summaries
- Top merchants
- Risk level assessment
- Narrative explanations

Example:

```json
{
  "total_spend_inr": 35600,
  "total_spend_usd": 450,
  "top_3_merchants": [
    "Swiggy",
    "Amazon",
    "IRCTC"
  ],
  "anomaly_count": 4,
  "narrative": "Most spending occurred on food and shopping. A few anomalous transactions were detected.",
  "risk_level": "Medium"
}
```

---

## Summary Statistics

Generated automatically for each job:

- Total transactions
- Total amount
- Successful transactions
- Failed transactions
- Duplicate count
- Anomaly count

---

## Run Locally

Clone repository:

```bash
git clone https://github.com/Ayushkumar20045/alemeno-finops.git
```

Move into project directory:

```bash
cd alemeno-finops
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI server:

```bash
uvicorn main:app --reload
```

Run Celery worker:

```bash
celery -A app.celery_app worker --loglevel=info
```

---

## Docker Setup

Build and start containers:

```bash
docker-compose up --build
```

Services:

- FastAPI API
- PostgreSQL
- Redis
- Celery Worker

---

## Database Models

### Job

Stores:

- Filename
- Status
- Row counts
- Created time
- Completed time
- Error messages

### Transaction

Stores:

- Transaction ID
- Date
- Merchant
- Amount
- Currency
- Status
- Category
- Account ID
- Notes
- Anomaly information

### Job Summary

Stores:

- Total transactions
- Total amount
- Success count
- Failure count
- Duplicate count
- Anomaly count

### Insight

Stores:

- Total INR spend
- Total USD spend
- Top merchants
- Anomaly count
- Narrative summary
- Risk level

---

## Author

**Ayush Kumar**

B.Tech Computer Science and Engineering (Data Science)

---

## Repository

GitHub:

```text
https://github.com/Ayushkumar20045/alemeno-finops
```

---

## License

This project is developed for educational and learning purposes.
