FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Grant execute permission to your script
RUN chmod +x start.sh

EXPOSE 8011

# Use the script as the entry point
CMD ["./start.sh"]
