# Technical Stack

## Airbyte Core Backend

- [Java 21](https://jdk.java.net/archive/)
- [Kotlin](https://kotlinlang.org/) for socket mode components
- Framework: [Micronaut](https://micronaut.io/)
- API: [OAS3](https://www.openapis.org/)
- Databases: [PostgreSQL](https://www.postgresql.org/)
- Unit & E2E testing: [JUnit 5](https://junit.org/junit5)
- Orchestration: [Temporal](https://temporal.io)
- Data serialization: [Protocol Buffers](https://protobuf.dev/) for high-performance socket mode
- Inter-process communication: Unix domain sockets for direct source-to-destination data transfer

## Connectors

Connectors can be written in any language. However the most common languages are:

- Python 3.9 or higher
- [Java 21](https://jdk.java.net/archive/)

## **Frontend**

- [Node.js](https://nodejs.org/en/)
- [TypeScript](https://www.typescriptlang.org/)
- Web Framework/Library: [React](https://reactjs.org/)

## Additional Tools

- CI/CD: [GitHub Actions](https://github.com/features/actions)
- Containerization: [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- Linter \(Frontend\): [ESLint](https://eslint.org/)
- Formatter \(Frontend & Backend\): [Prettier](https://prettier.io/)
- Formatter \(Backend\): [Spotless](https://github.com/diffplug/spotless)
