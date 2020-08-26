# Getting Started

Run

```bash
docker-compose up
```

Go to [http://localhost:8000](http://localhost:8000)

Update public images:

```bash
docker-compose -f docker-compose.yaml -f docker-compose.build.yaml build
docker-compose -f docker-compose.yaml -f docker-compose.build.yaml push
```

