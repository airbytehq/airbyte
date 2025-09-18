# README for Destination MockAPI Connector

## Overview

The Destination MockAPI Connector is designed to facilitate the integration of data from various Airbyte sources into a mock API provided by [MockAPI](https://mockapi.io/). This connector allows users to map their data into predefined schemas, specifically for users and deals, making it easy to test and simulate API interactions.

## Features

- **Data Mapping**: Supports mapping of data from Airbyte sources into user and deal schemas.
- **API Interaction**: Handles API requests to MockAPI, allowing for easy data submission.
- **Configuration Management**: Provides a straightforward way to configure the connector with necessary API settings.

## Project Structure

```
destination-mockapi
├── src
│   └── destination_mockapi
│       ├── __init__.py
│       ├── client.py
│       ├── config.py
│       ├── destination.py
│       ├── run.py
│       ├── writer.py
│       └── schemas
│           ├── __init__.py
│           ├── users.py
│           └── deals.py
├── unit_tests
│   ├── __init__.py
│   ├── test_mockapi_client.py
│   ├── test_mockapi_config.py
│   ├── test_mockapi_destination.py
│   ├── test_mockapi_writer.py
│   └── test_schemas.py
├── integration_tests
│   └── test_integration.py
├── acceptance-test-config.yml
├── main.py
├── pyproject.toml
├── poetry.lock
├── metadata.yaml
├── icon.svg
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd destination-mockapi
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

## Configuration

Before running the connector, you need to configure the API settings. Update the `acceptance-test-config.yml` file with your MockAPI URL and API key.

## Usage

To run the connector, execute the following command:
```
python main.py
```

This will start the destination connector and begin processing data from Airbyte sources.

## Testing

### Unit Tests

To run unit tests, use:
```
pytest unit_tests/
```

### Integration Tests

To run integration tests, use:
```
pytest integration_tests/
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [Airbyte](https://airbyte.com/) for providing the framework for building connectors.
- [MockAPI](https://mockapi.io/) for offering a simple way to mock APIs for testing purposes.