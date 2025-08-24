# Food Truck Search API

A modern FastAPI service that provides comprehensive food truck search capabilities with automatic data reloading.

## Project Structure

This is a FastAPI framework based project. 

```
.
├── app/                    # Main application
│   ├── main.py            # FastAPI app
│   ├── api/               # API endpoints
│   ├── models/            # Data models
│   ├── dataloader/        # Business logic
│   ├── utils/             # Functions that 
│   └── static/            # Frontend UI
├── datastore/             # Data source
├── tests/                 # Unit tests
├── requirements.txt        # Dependencies
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

### 3. Open the UI

Once the container is running, you can access the web interface at:
```
http://localhost:8000
```
### 4. Test the API

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

## Testing

The project includes comprehensive unit tests for all components:

### Running Tests

1. **Install test dependencies:**
   
   **(Recommended):**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run all tests:**
   ```bash
   python run_tests.py
   # or
   python -m pytest tests/ -v
   ```

3. **Run specific test files:**
   ```bash
   python run_tests.py tests/test_models.py
   python run_tests.py tests/test_api.py
   ```

4. **Run specific test functions:**
   ```bash
   python -m pytest tests/test_models.py::TestSearchRequest::test_valid_name_search -v
   ```



## System Design

### Requirements

#### Functional Requirements

- As a client, I should be able to search for food facility permits by applicant name.
- As a client, I should be able to search for food facility permits by street name, using either a partial or full match.
- As a client, I should be able to retrieve the 5 nearest food facility locations by providing latitude and longitude.
- As a service, I should by default return only results with status "APPROVED" when searching for the nearest 5 locations, but allow the client to override this filter to include all statuses.
- As a service, I should provide automated tests that cover valid inputs, invalid inputs, and filtering logic.

#### Non-Functional Requirements

- The environment should be containerized using a Dockerfile.
- A user interface (UI) should be provided for interacting with the service.
- An automatic documentation tool should be integrated for API/service documentation.

### Technical Architecture Decisions

#### Distance Calculation
- **Haversine Formula**: Implemented for calculating distances between geographic coordinates, providing accurate approximations for Earth's spherical surface

#### Data Processing Strategy
- **In-Memory Processing**: Chosen for optimal performance with the provided dataset size, eliminating I/O bottlenecks
- **Pandas Integration**: Leveraged for efficient data manipulation and analysis capabilities

#### Framework Selection
- **FastAPI**: Selected over Flask for its built-in automatic API documentation generation, enhancing developer experience and API discoverability 


Critique section:
What would you have done differently if you had spent more time on this?

What are the trade-offs you might have made?

What are the things you left out?

What are the problems with your implementation and how would you solve them if we had to scale the application to a large number of users?



1. I will do a lot of things differently if i have more time on this. Please check the below Long term plan and 