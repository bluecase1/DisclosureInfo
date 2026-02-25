FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -U pip

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -e .

COPY src /app/src

EXPOSE 8000
CMD ["uvicorn", "disclosureinfo.main:app", "--host", "0.0.0.0", "--port", "8000"]
