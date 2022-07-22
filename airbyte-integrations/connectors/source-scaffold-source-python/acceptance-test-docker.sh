#!/usr/bin/env sh

# Set this variable to false to bypass spec backward compatibility checks
RUN_SPEC_BACKWARD_COMPATIBILITY_TEST=true

# Build latest connector image
docker build . -t $(cat acceptance-test-config.yml | grep "connector_image" | head -n 1 | cut -d: -f2-)

# Pull latest source-acceptance-test image
docker pull airbyte/source-acceptance-test:latest

TEST_OPTIONS="--acceptance-test-config /test_input"
if [ "$RUN_SPEC_BACKWARD_COMPATIBILITY_TEST" = false ] ; then
    echo "Won't run spec backward compatibility tests"
    # Add a -m flag to pytest options to not run tested with spec_backward_compatibility marker
    TEST_OPTIONS+='-m "not spec_backward_compatibility"'
fi

# Run
docker run --rm -it \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $(pwd):/test_input \
    airbyte/source-acceptance-test \
    ${TEST_OPTIONS}

