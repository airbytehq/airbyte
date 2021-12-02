image_name = dm/airbyte-destination-intercom
aws_account_id = 027405332109
aws_profile = default
region = ap-southeast-1
repository_uri = $(aws_account_id).dkr.ecr.$(region).amazonaws.com/$(image_name)
image_tag = $(shell date +%m%d%Y.%H%M%S)

echo-tag:
	echo $(image_tag)

docker-build: 
	docker build -t $(image_name):latest -t $(image_name):$(image_tag) .
	
docker-push:
	make docker-build
	docker tag $(image_name) $(repository_uri)
	docker tag $(image_name):$(image_tag) $(repository_uri):$(image_tag)
	docker login -u AWS -p `aws ecr get-login-password --region $(region) --profile $(aws_profile)` $(repository_uri)
	docker push $(repository_uri):latest
	docker push $(repository_uri):$(image_tag)
