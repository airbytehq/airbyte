# Technical Stack

## Airbyte Core Backend

- [Java 21](https://jdk.java.net/archive/)
- Framework: [Micronaut](https://micronaut.io/)
- API: [OAS3](https://www.openapis.org/)
- Databases: [PostgreSQL](https://www.postgresql.org/)
- Unit & E2E testing: [JUnit 5](https://junit.org/junit5)
- Orchestration: [Temporal](https://temporal.io)

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

## FAQ

### _Why do we write most destination/database connectors in Java?_

JDBC makes writing reusable database connector frameworks fairly easy, saving us a lot of development time.

### _Why are most REST API connectors written in Python?_

Most contributors felt comfortable writing in Python, so we created a [Python CDK](../connector-development/cdk-python/) to accelerate this development. You can write a connector from scratch in any language as long as it follows the [Airbyte Specification](airbyte-protocol.md).

### _Why did we choose to build the server with Java?_

Simply put, the team has more experience writing production Java code.

### _Why do we use_ [_Temporal_](https://temporal.io) _for orchestration?_

Temporal solves the two major hurdles that exist in orchestrating hundreds to thousands of jobs simultaneously: scaling state management and proper queue management. Temporal solves this by offering primitives that allow serialising the jobs' current runtime memory into a DB. Since a job's entire state is stored, it's trivial to recover from failures, and it's easy to determine if a job was assigned correctly.
