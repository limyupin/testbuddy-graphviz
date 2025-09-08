#!/bin/bash
# Build script for Render deployment
# This installs system dependencies including Graphviz

echo "Installing system dependencies..."

# Update package list
apt-get update

# Install Graphviz and other dependencies
apt-get install -y graphviz graphviz-dev

# Verify Graphviz installation
which dot
dot -V

echo "Installing Python dependencies..."
# Install Python dependencies
pip install -r requirements.txt

echo "Build completed successfully!"
