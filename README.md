# Food Truck Search API

A modern FastAPI service that provides comprehensive food truck search capabilities with automatic data reloading.

## Project Structure

```
.
├── app/                    # Main application package
│   ├── __init__.py        # App package initialization
│   ├── main.py            # FastAPI application entry point
│   ├── models/            # Data models package
│   │   ├── __init__.py    # Models package
│   │   └── food_truck.py  # Food truck and search models
│   ├── api/               # API endpoints package
│   │   ├── __init__.py    # API package
│   │   ├── search.py      # Unified search endpoint
│   │   └── health.py      # Health check endpoint
│   ├── dataloader/        # Data loading package
│   │   ├── __init__.py    # DataLoader package
│   │   └── food_truck_loader.py # CSV data loader with auto-reload
│   ├── utils/             # Utility functions package
│   │   ├── __init__.py    # Utils package
│   │   ├── geo.py         # Geography utilities (Haversine distance)
│   │   ├── search.py      # Search logic functions
│   │   └── mappers.py     # Data transformation utilities
│   └── static/            # Frontend static files
│       ├── index.html     # Main web interface
│       ├── styles.css     # Styling
│       └── script.js      # Frontend JavaScript
├── datastore/             # Data files
│   └── Mobile_Food_Facility_Permit_20250822.csv
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

## Running with Docker

### 1. Build the Docker Image

```bash
docker build -t flask-restaurant-api .
```

### 2. Run the Container

```bash
docker run -d -p 8000:8000 --name restaurant-api flask-restaurant-api
```

### 3. Access the Web Interface

Once the container is running, you can access the web interface at:
```
http://localhost:8000
```

The web interface provides:
- **Tabbed search interface** for different search types
- **Modern, responsive design** that works on all devices
- **Interactive forms** for name, street, and proximity searches
- **Beautiful results display** with food truck cards
- **Quick actions** like using your current location or random SF coordinates

This will:
- Start the container in detached mode (`-d`)
- Map port 5000 from the container to port 5000 on your host (`-p 5000:5000`)
- Name the container `restaurant-api` for easy reference

### 3. Test the API

Once the container is running, you can test the API using curl:

```bash
curl -X POST http://localhost:8000/api/getRestaurant \
  -H "Content-Type: application/json" \
  -d '{"keywords": "pizza"}'
```

Expected response:
```json
{
  "success": true,
  "message": "Restaurant search completed",
  "keywords": "pizza",
  "restaurants": []
}
```

## Container Management

### Stop the container:
```bash
docker stop restaurant-api
```

### Start the container again:
```bash
docker start restaurant-api
```

### Remove the container:
```bash
docker rm restaurant-api
```

### View container logs:
```bash
docker logs restaurant-api
```

## API Endpoints

### GET /docs
Get the OpenAPI specification in JSON format.

### GET /docs/swagger
Interactive Swagger UI for testing and exploring the API.

### GET /api/health
Health check endpoint to verify the service is running.

### POST /api/search

**Request Body:**
```json
{
  "query_type": "name" | "street" | "proximity",
  "applicant": "string",          # Required for name search
  "street": "string",             # Required for street search
  "latitude": float,              # Required for proximity search
  "longitude": float,             # Required for proximity search
  "status": "APPROVED" | "REQUESTED" | "EXPIRED",  # Optional filter
  "limit": int                    # Optional, default 10, max 100
}
```

**Response:**
```json
{
  "success": boolean,
  "message": "string",
  "data": [
    {
      "locationid": "string",
      "applicant": "string",
      "facility_type": "string",
      "address": "string",
      "status": "string",
      "food_items": "string",
      "latitude": float,
      "longitude": float,
      "location_description": "string"
    }
  ],
  "metadata": {
    "total_results": int,
    "query_type": "string",
    "status_filter": "string",
    "limit": int
  }
}
```

**Example Usage:**

1. **Search by business name:**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query_type": "name", "applicant": "Philz", "status": "APPROVED"}'
```

2. **Search by street:**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query_type": "street", "street": "SANSOME", "limit": 5}'
```

3. **Search by proximity:**
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query_type": "proximity", "latitude": 37.7749, "longitude": -122.4194, "limit": 5}'
```

## Development

The API currently returns immediately with placeholder data. You can add your restaurant search logic in the `get_restaurant()` function in `app.py` where the TODO comment is located.
