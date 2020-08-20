# Getting Started

Run

```bash
./tools/app/build.sh
./tools/app/start.sh
```

Go to [http://localhost:8000](http://localhost:8000)

Update public images:

```bash
./tools/app/build.sh
docker-compose -f docker-compose.dev.yaml -f docker-compose.dist.yaml push
```

