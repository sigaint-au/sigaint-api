# Use an official Python runtime as the base image
FROM registry.access.redhat.com/ubi10/ubi:latest


RUN dnf -y install python3-pip sudo openldap-clients && \
    dnf clean all

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory (our Flask app) into the container at /app
COPY . /app
COPY ca.crt /etc/pki/ca-trust/source/anchors/ca.crt

RUN update-ca-trust

# Install Flask and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available for the app
EXPOSE 5000

# Run the command to start the Flask
CMD ["flask", "run", "--host=0.0.0.0"]