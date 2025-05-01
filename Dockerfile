FROM python:3.11-slim  

WORKDIR /app

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8005"]