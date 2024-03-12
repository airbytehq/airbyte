#!/bin/bash

# Set root to airbyte-cdk: needed for 2,
ROOT_DIR=$(cd ../../ && pwd)
export ROOT_DIR

# 1. generateCodeGeneratorImage
echo "Generating code generator image..."
bin/build_code_generator_image.sh
echo "Done generating code generator image."


# 2. generateComponentManifestClassFiles
echo "Generating component manifest files..."
bin/generate-component-manifest-files.sh
echo "Done generating component manifest files."
