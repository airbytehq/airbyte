SHELL=/bin/bash



.PHONY: connectors_mypy
connectors_mypy:
	python -m pip install nox
	if [ $(source) ]; then \
		pushd airbyte-integrations/bases/base-python && \
		nox --session "mypy($(source))" && \
		popd; \
	else \
		pushd airbyte-integrations/bases/base-python && \
		nox && \
		popd; \
	fi

.PHONY: connectors_test
connectors_test:
	python -m pip install nox
	if [ $(source) ]; then \
		pushd airbyte-integrations/bases/base-python && \
		nox --session "tests($(source))" && \
		popd; \
	else \
		pushd airbyte-integrations/bases/base-python && \
		nox && \
		popd; \
	fi
