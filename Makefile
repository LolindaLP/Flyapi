.PHONY: run

# Define the default target
run:
	@echo "Activating virtual environment..."
	@source .venv/scripts/activate && \
	cd app && \
	echo "Running FastAPI..." && \
	python -m uvicorn main:app --reload
