# Conduit
## Getting Started

### Docker
```
docker run --rm -it dataline/conduit:$VERSION
```

### Repo
```
VERSION=$(cat .version)
docker build . -t dataline/conduit:$VERSION
docker run --rm -it dataline/conduit:$VERSION
```
