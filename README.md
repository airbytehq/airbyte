# Getting Started

Simply run

```bash
./tools/app/start.sh
```

Go to [http://localhost:8000](http://localhost:8000)

Update public images:

```bash
docker-compose -f docker-compose.dev.yaml -f docker-compose.dist.yaml push
```

