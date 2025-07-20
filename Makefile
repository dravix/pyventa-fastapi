include .env
export

.PHONY: run

run:
	uvicorn main:app --reload

.PHONY: dev

dev:		# Start the development server
	source venv/bin/activate && fastapi run --reload app/main.py
