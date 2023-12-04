# Use the official Python image
FROM python:3.9

# Set the working directory in the container
WORKDIR .

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8002

# Command to run on container start
CMD ["python", "main.py"]