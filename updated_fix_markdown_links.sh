#!/bin/bash

# Script to fix broken Markdown links in /docs/integrations/ folder
# This will update links that point to files now in /docs/platform/
# Excludes .gitbook paths, /integrations/ paths, and /release_notes/ paths

# Find all Markdown files in the /docs/integrations/ directory
find /home/ubuntu/repos/airbyte/docs/integrations -type f -name "*.md" | while read -r file; do
  echo "Processing $file"
  
  # Fix relative links with pattern ../../understanding-airbyte/file.md
  sed -i 's|\(\[.*\]\s*(\)../../understanding-airbyte/|\1../../platform/understanding-airbyte/|g' "$file"
  
  # Fix relative links with pattern ../../operator-guides/file.md
  sed -i 's|\(\[.*\]\s*(\)../../operator-guides/|\1../../platform/operator-guides/|g' "$file"
  
  # Fix relative links with pattern ../../connector-development/file.md
  sed -i 's|\(\[.*\]\s*(\)../../connector-development/|\1../../platform/connector-development/|g' "$file"
  
  # Fix absolute links with pattern /understanding-airbyte/file.md
  sed -i 's|\(\[.*\]\s*(\)/understanding-airbyte/|\1/platform/understanding-airbyte/|g' "$file"
  
  # Fix absolute links with pattern /operator-guides/file.md
  sed -i 's|\(\[.*\]\s*(\)/operator-guides/|\1/platform/operator-guides/|g' "$file"
  
  # Fix absolute links with pattern /connector-development/file.md
  sed -i 's|\(\[.*\]\s*(\)/connector-development/|\1/platform/connector-development/|g' "$file"
  
  # Fix absolute links with pattern /using-airbyte/file.md
  sed -i 's|\(\[.*\]\s*(\)/using-airbyte/|\1/platform/using-airbyte/|g' "$file"
  
  # Undo any changes to .gitbook paths
  sed -i 's|\(\[.*\]\s*(\)/platform/.gitbook/|\1/.gitbook/|g' "$file"
  
  # Undo any changes to /integrations/ paths
  sed -i 's|\(\[.*\]\s*(\)/platform/integrations/|\1/integrations/|g' "$file"
  
  # Undo any changes to /release_notes/ paths
  sed -i 's|\(\[.*\]\s*(\)/platform/release_notes/|\1/release_notes/|g' "$file"
  sed -i 's|\(\[.*\]\s*(\)../../platform/release_notes/|\1../../release_notes/|g' "$file"
done

echo "Link fixes completed"
