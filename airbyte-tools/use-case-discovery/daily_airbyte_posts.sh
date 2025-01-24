#!/bin/bash

# Activate virtual environment
source /home/ubuntu/.venv/bin/activate

# Change to the working directory
cd /home/ubuntu

# Run the content generation script
python content_generation_agent.py >> /home/ubuntu/airbyte_posts.log 2>&1

# Add timestamp to log
echo "Run completed at $(date)" >> /home/ubuntu/airbyte_posts.log
