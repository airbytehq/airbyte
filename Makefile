##@ Makefile

##@ Define the default version
VERSION ?= latest

tools.airbyte-ci.install: ## Install airbyte-ci
	##@ Determine the operating system and download the binary
	@OS=$$(uname); \
	if [ "$$OS" = "Linux" ]; then \
		URL="https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/airbyte-ci/releases/ubuntu/${VERSION}/airbyte-ci"; \
		echo "Linux based system detected. Downloading from $$URL"; \
	elif [ "$$OS" = "Darwin" ]; then \
		URL="https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/airbyte-ci/releases/macos/${VERSION}/airbyte-ci"; \
		echo "macOS based system detected. Downloading from $$URL"; \
	else \
		echo "Unsupported operating system"; \
		exit 1; \
	fi; \
	curl -L -f $$URL -o ~/.local/bin/airbyte-ci; \

	##@ Create the directory if it does not exist and make the binary executable
	mkdir -p ~/.local/bin && chmod +x ~/.local/bin/airbyte-ci; \
	echo "╔─────────────────────────────────────────────────────────────────────────────────────────────────╗"; \
	echo "│                                                                                                 │"; \
	echo "│                                                                                                 │"; \
	echo "│    /$$$$$$  /$$$$$$ /$$$$$$$  /$$$$$$$  /$$     /$$ /$$$$$$$$ /$$$$$$$$       /$$$$$$  /$$$$$$  │"; \
	echo "│   /$$__  $$|_  $$_/| $$__  $$| $$__  $$|  $$   /$$/|__  $$__/| $$_____/      /$$__  $$|_  $$_/  │"; \
	echo "│  | $$  \ $$  | $$  | $$  \ $$| $$  \ $$ \  $$ /$$/    | $$   | $$           | $$  \__/  | $$    │"; \
	echo "│  | $$$$$$$$  | $$  | $$$$$$$/| $$$$$$$   \  $$$$/     | $$   | $$$$$ /$$$$$$| $$        | $$    │"; \
	echo "│  | $$__  $$  | $$  | $$__  $$| $$__  $$   \  $$/      | $$   | $$__/|______/| $$        | $$    │"; \
	echo "│  | $$  | $$  | $$  | $$  \ $$| $$  \ $$    | $$       | $$   | $$           | $$    $$  | $$    │"; \
	echo "│  | $$  | $$ /$$$$$$| $$  | $$| $$$$$$$/    | $$       | $$   | $$$$$$$$     |  $$$$$$/ /$$$$$$  │"; \
	echo "│  |__/  |__/|______/|__/  |__/|_______/     |__/       |__/   |________/      \______/ |______/  │"; \
	echo "│                                                                                                 │"; \
	echo "│   Installation completed.                                                                       │"; \
	echo "╚─────────────────────────────────────────────────────────────────────────────────────────────────╝";

tools.airbyte-ci-dev.install: ## Install the development version of airbyte-ci
	##@ Install airbyte-ci development version
	pipx install --editable --force --python=python3.10 airbyte-ci/connectors/pipelines/; \
	echo "Development version of airbyte-ci installed.";

tools.check.airbyte-ci: # Check if airbyte-ci is installed correctly
	##@ Check if airbyte-ci is on the PATH and pointing to the correct location
	@EXPECTED_PATH="$$HOME/.local/bin/airbyte-ci"
	AIRBYTE_CI_PATH=$$(which airbyte-ci 2>/dev/null)
	if [ "$$AIRBYTE_CI_PATH" != "$$EXPECTED_PATH" ]; then \
		echo "airbyte-ci is either not on the PATH or not pointing to $$EXPECTED_PATH"; \
		echo "Check that airbyte-ci exists at $$HOME/.local/bin and $$HOME/.local/bin is part the PATH"; \
		echo "If it does try running removing all instances of airbyte-ci on your path, then run `make tools.install` again"; \
		exit 1; \
	fi; \
	echo "airbyte-ci is correctly installed at $$EXPECTED_PATH"


tools.install: tools.airbyte-ci.install tools.check.airbyte-ci

.PHONY: tools.install tools.airbyte-ci.install tools.airbyte-ci-dev.install

