#!/bin/sh
set -e

# Start ollama in the background
ollama serve &

# Wait until Ollama API is ready
until curl -s http://localhost:11434/api/tags > /dev/null; do
  echo "Waiting for Ollama to start..."
  sleep 2
done

# Pull your models
ollama pull nomic-embed-text
ollama pull llama3.2:latest

wait
