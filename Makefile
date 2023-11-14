# Makefile

# Define the install command
tools.install:
	# Determine the operating system and download the binary
	@OS=$$(uname); \
	if [ "$$OS" = "Linux" ]; then \
		echo "Linux based system detected"; \
		curl -L https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/airbyte-ci/releases/ubuntu/latest/airbyte-ci -o ~/.local/bin/airbyte-ci; \
	elif [ "$$OS" = "Darwin" ]; then \
		echo "macOS based system detected"; \
		curl -L https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/airbyte-ci/releases/macos/latest/airbyte-ci -o ~/.local/bin/airbyte-ci; \
	else \
		echo "Unsupported operating system"; \
		exit 1; \
	fi; \
	# Create the directory if it does not exist and make the binary executable
	mkdir -p ~/.local/bin && chmod +x ~/.local/bin/airbyte-ci; \
	echo "Installation completed."

.PHONY: tools.install

