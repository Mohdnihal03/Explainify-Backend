#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data (required for semantic chunking)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create necessary directories
mkdir -p transcripts chunks chroma_db

echo "✅ Build completed successfully!"
