# Official Apify Python 3.11 base image
FROM apify/actor-python:3.11

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Actor project files
COPY . ./

# Execute the Actor main module
CMD ["python3", "-m", "src.main"]
