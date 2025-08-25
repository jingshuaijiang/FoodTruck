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
   docker exec food-truck-api python -m pytest tests/ -v
   ```

2. **Run all tests:**
   ```bash
   docker exec food-truck-api python run_tests.py
   # or
   docker exec food-truck-api python -m pytest tests/ -v
   ```

3. **Run specific test files:**
   ```bash
   docker exec food-truck-api python run_tests.py tests/test_models.py
   docker exec food-truck-api python run_tests.py tests/test_api.py
   ```

4. **Run specific test functions:**
   ```bash
   docker exec food-truck-api python -m pytest tests/test_models.py::TestSearchRequest::test_valid_name_search -v
   ```



## System Design for my implementation

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
- **Data Refreshing**: In memory data refreshed every 1 min

#### Framework Selection
- **FastAPI**: Selected over Flask for its built-in automatic API documentation generation, enhancing developer experience and API discoverability 


## Critique section:
### 1. What would you have done differently if you had spent more time on this?
**See the [Long-Term Architecture Plan](#long-term-architecture-plan) section below for detailed technical specifications and scaling strategies.**


### 2. What are the trade-offs you might have made?
**Data Storage Trade-offs:**
- **In-Memory vs. Database**: Chose in-memory for rapid development but sacrificed scalability and flexibility

**Scalability Trade-offs:**
- **Current vs. Production-Ready**: Current implementation optimized for small datasets, lacks support for large-scale operations

### 3. What are the things you left out?
1. Authorization and authentication. 
2. Rate limiting. 
3. Pagination. 
4. ORR (Metrics and alarms)

### 4. What are the problems with your implementation and how would you solve them if we had to scale the application to a large number of users?

**See the [Long-Term Architecture Plan](#long-term-architecture-plan) section below for detailed technical specifications and scaling strategies.**



# Long-Term Architecture Plan

## High-Level Design (HLD)

### Design Assumptions

- **Data Volume**: System designed to handle terabyte-scale datasets
- **Performance Requirements**: P90 response time target of 50ms
- **Data Stability**: Source data exhibits low volatility with infrequent updates 

![HLD Workflow](HLD_workflow.svg)

1. Customer send request to a load balancer. 
2. Load balancer distributed traffic to different AWS ECS fargate. 
3. Fargate container will check the cache(Redis) for the query parameter first. If cache hit, then immediately return the response. 
4. If cache does not contains the corresponding result then fall back to the database (Postgre SQL).
5. Each customer query will become an event stream and asynchonously inserted into a datalake system. 
6. The datalake system will do the weekly(I don't want it to be daily unless statistics shows user query pattern changed everyday.) job to get the top query patterns and use someway to warm the redis cache based on those result. 

### Caching Strategy

**Search Query Caching**
- **Applicant Name & Street Search**: Implement streaming events to asynchronously collect top 10,000 frequently queried parameters and populate cache. Each customer query becomes an event stream and asynchronously inserted into a datalake system for weekly analysis of top query patterns to warm the Redis cache.
- **Geographic Search**: Pre-calculate food truck locations for each geohash (gh7/gh8) region. When a proximity query arrives, translate coordinates to geohash, query neighboring regions from cache, and return food trucks meeting requirements (status, distance limits).

**Database Fallback**
- **PostgreSQL Integration**: Store uncached data in PostgreSQL for persistent storage
- **Hybrid Approach**: Cache for performance, database for persistence and complex queries
### Data store choices

#### NoSQL Database
- **DynamoDB Limitations**: DynamoDB lacks native support for complex column operations, making it suitable only for metadata storage, not for this specific use case

#### In-Memory Database
- **Cost Considerations**: Storing the entire dataset in memory (especially for TB-scale data) can be prohibitively expensive
- **Performance Trade-offs**: Only necessary when strict performance requirements justify the additional infrastructure costs

#### SQL Database
- **PostgreSQL Selection**: PostgreSQL provides optimal internal indexing capabilities for our specific use case requirements 


### Database Indexing Strategy

**Text Search Indexes**
- **Applicant Name**: B-tree index with `btree(lower(applicant))` for prefix matching

**Street Search Indexes**
- **Partial Matching**: GIN index with `gin_trgm_ops` for case-insensitive partial string matching
- **Pattern Support**: Enables queries like `'%san%'` for substring searches

**Geographic Indexes**
- **K-Nearest Neighbor (KNN)**: GiST index on geometry column with `ORDER BY geom <-> point` for proximity searches




