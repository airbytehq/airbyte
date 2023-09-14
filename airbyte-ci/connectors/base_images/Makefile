all: build
lock: 
	poetry lock
install: lock
	poetry install
build: install
	poetry run build
	git add generated