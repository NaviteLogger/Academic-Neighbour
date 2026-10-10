FROM python:3.15-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync

COPY . /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]