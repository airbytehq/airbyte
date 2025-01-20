# 変数定義
VERSION = 0.0.9
IMAGE_NAME = yyoshimura0801/rakuten-rms
SOURCE_NAME = source-rakuten-rms
CONNECTOR_NAME = source-rakuten-rms
ECR_REPO = 058264134174.dkr.ecr.ap-northeast-1.amazonaws.com/rakuten-rms-repo

.PHONY: all clean build tag push test spec discover test1 

all: clean build tag push test spec discover

spec:
	@echo "Running spec..."
	poetry run $(SOURCE_NAME) spec

discover:
	@echo "Running discover..."
	poetry run $(SOURCE_NAME) discover --config secrets/config.json

test:
	@echo "Running tests..."
	poetry run $(SOURCE_NAME) read --config secrets/config.json --catalog integration_tests/configured_catalog.json

test1:
	poetry run $(SOURCE_NAME) read --config secrets/config.json --catalog integration_tests/configured_catalog_purchase_order.json --debug 

help:
	@echo "Usage: make [command]"
	@echo "Commands:"
	@echo "  all: build, tag, push, test, spec, discover"
	@echo "  clean: remove Docker images"
	@echo "  build: build the project"
	@echo "  tag: tag the Docker image"
	@echo "  push: push the Docker image"
	@echo "  build_and_push: build, tag, and push the Docker image"
	@echo "  test: run tests"
	@echo "  spec: run spec"
	@echo "  discover: run discover"

clean:
	@echo "Cleaning up..."
	docker image prune -f
# docker rmi $(IMAGE_NAME):$(VERSION) || true

# コマンド1: ビルド
build:
	@echo "Building the project..."
	airbyte-ci connectors --name=$(CONNECTOR_NAME) build

# コマンド2: タグ
tag:
	@echo "Tagging the Docker image..."
	@echo "Source: airbyte/$(CONNECTOR_NAME):dev"
	@echo "Target: $(IMAGE_NAME):$(VERSION)"
	docker tag airbyte/$(CONNECTOR_NAME):dev $(ECR_REPO):$(VERSION)

# コマンド3: プッシュ
push: tag
	@echo "Pushing the Docker image..."
	@echo command1 || command2
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 058264134174.dkr.ecr.ap-northeast-1.amazonaws.com
	docker push $(ECR_REPO):$(VERSION)

# ビルド・タグ付け・プッシュを同時に行う
build_and_push: build tag push
	@echo "Build, tag, and push completed."