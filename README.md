# Pulse Price AI
This project consists of two independent services: a standalone ETL pipeline that uses a generative AI to collect agricultural market data, and a separate FastAPI web service that provides read-only access to that data.

# System Architecture
- The system is designed with a decoupled architecture, separating the data ingestion (write) process from the data serving (read) process. The following diagram illustrates the flow of data between the components.


 ![System Design Diagram](https://github.com/Orusaki-tech/ai-hack/blob/main/PulsePrice%20AI%20SD.png)


## Technology Stack
- Web Framework: FastAPI
- Database ORM: SQLAlchemy
- Data Validation: Pydantic
- Generative AI: Google Gemini
- Database: SQLite


## API Endpoints
- The API provides the following read-only endpoints:

- **Get All Market Data**
-GET /market-data/
- **Description**: Retrieves a list of all market data records currently stored in the database.

- **Get Market Data by ID**
- GET /market-data/{item_id}
**Description**: Retrieves a single market data record by its unique ID.
