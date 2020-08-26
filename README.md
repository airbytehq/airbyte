# Getting Started

Run

```bash
docker-compose up
```

Go to [http://localhost:8000](http://localhost:8000)

Update public images:

```bash
./tools/app/build.sh
./tools/app/test.sh
docker-compose -f docker-compose.dev.yaml -f docker-compose.dist.yaml push
```

