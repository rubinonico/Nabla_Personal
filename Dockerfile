# Use the official N8N image as the base
FROM docker.n8n.io/n8nio/n8n:latest

# Switch to the root user to install system packages
USER root

# Install Python, pip, and essential build tools
RUN apk add --no-cache python3 py3-pip build-base python3-dev

# Copy the Python dependency list into the container
COPY requirements.txt .

# Install the specified Python libraries
RUN pip install --break-system-packages -r requirements.txt

# *** ADD THIS LINE to copy your scripts ***
COPY scripts/ /scripts/

# Switch back to the non-privileged 'node' user for security

USER node
