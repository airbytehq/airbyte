# Conduit
## First run
```
VERSION=$(cat .version)
docker build . -t conduit:$VERSION
docker run --rm -it conduit:$VERSION
```
