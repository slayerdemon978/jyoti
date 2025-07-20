FROM --platform=linux/amd64 python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the processing script
COPY process_pdfs.py .

# Make the script executable
RUN chmod +x process_pdfs.py

# Run the script
CMD ["python", "process_pdfs.py"]