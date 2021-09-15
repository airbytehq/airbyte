RELEASE_NAME := airbyte
NAMESPACE := airbyte

lint:
	helm lint .


install:
	helm upgrade --install \
				--create-namespace \
				--namespace $(NAMESPACE) \
				--debug \
				--wait \
				--timeout 600s \
				$(RELEASE_NAME) .


test:
	helm test $(RELEASE_NAME) --logs --debug --namespace $(NAMESPACE)


diagnostics:
	kubectl -n $(NAMESPACE) get pods -o wide
	kubectl -n $(NAMESPACE) get pods --no-headers | grep -v "Running" | awk '{print $$1}' | xargs -L 1 -r kubectl -n $(NAMESPACE) logs


template:
	helm template --release-name $(RELEASE_NAME) .


# Uses the readme-generator command to update the README.md
# with changes in the values.yaml file. See: https://github.com/bitnami-labs/readme-generator-for-helm
update-docs:
	readme-generator -v ./values.yaml -r README.md
