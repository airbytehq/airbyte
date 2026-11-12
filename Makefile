##@ Makefile

## Detect the operating system
OS := $(shell uname)

tools.git-hooks.clean: ## Clean git hooks
	@echo "Unset core.hooksPath"
	@git config --unset core.hooksPath || true
	@echo "Removing pre-commit hooks..."
	@pre-commit uninstall
	@echo "Removing pre-push hooks..."
	@rm -rf .git/hooks
	@echo "Git hooks removed."

tools.pre-commit.install.Linux:
	@echo "Installing pre-commit with pip..."
	@pip install --user pre-commit
	@echo "Pre-commit installation complete."

tools.pre-commit.install.Darwin:
	@echo "Installing pre-commit with brew..."
	@brew install pre-commit maven
	@echo "Pre-commit installation complete"

tools.git-hooks.install: tools.pre-commit.install.$(OS) tools.git-hooks.clean ## Setup pre-commit hooks
	@echo "Installing pre-commit hooks..."
	@pre-commit install --hook-type pre-push
	@echo "Pre-push hooks installed."

tools.install: tools.pre-commit.install.$(OS)

version.bulk.cdk:
	@echo "Latest version of the Bulk CDK is $(shell curl -k --silent "https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/io/airbyte/bulk-cdk/bulk-cdk-core-load/maven-metadata.xml" | sed -ne 's:.*<latest>\(.*\)</latest>:\1:p')"

.PHONY: tools.install tools.pre-commit.install tools.git-hooks.install tools.git-hooks.clean
