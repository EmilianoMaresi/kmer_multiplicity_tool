# Step 1: Use an official lightweight Python image
FROM python:3.11-slim

# Step 2: Install system dependencies required for compiling/running C++ tools like DoLIer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Set up the working directory inside the container
WORKDIR /app

# Step 4: Copy and install Python requirements first (speeds up rebuilds via caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your application code into the container
COPY . .

# Step 6: Make sure your Python script is executable
RUN chmod +x kmer_multiplicity_tool.py

# Step 7: Define the entrypoint so it runs your script automatically
ENTRYPOINT ["python", "kmer_multiplicity_tool.py"]
