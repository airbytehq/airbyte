#!/bin/bash

# Check if a file path is provided
if [ -z "$1" ]; then
    echo "Please provide a file path."
    exit 1
fi

# Initialize lists
succeeded=()
failed_ci_credentials=()
failed_validate_source=()
spec_only_succeeded_due_to_no_secrets=()
succeeded_spec_only=()
succeeded_spec_only_community=()

# Read each line from the file
while IFS= read -r directory; do
    directory="${directory%/}"
    echo "Processing directory: $directory"

    # Check if supportLevel is certified
    if ! grep -q "supportLevel: certified" "./airbyte-integrations/connectors/$directory/metadata.yaml"; then
        # Run only --validate-install-only for community connectors
        if airbyte-lib-validate-source --connector-dir "./airbyte-integrations/connectors/$directory/" --validate-install-only > "debug-validate-spec-$directory.txt" 2>&1; then
            succeeded_spec_only_community+=("$directory")
        else
            failed_validate_source+=("$directory")
            echo "validate-source --validate-install-only failed for $directory. Check debug-validate-spec-$directory.txt for details."
        fi
        rm -rf .venv-source-*
        continue
    fi

    ci_credentials_failed=false

    if ! VERSION=dev ci_credentials "$directory" write-to-storage > "debug-ci-credentials-$directory.txt" 2>&1; then
        ci_credentials_failed=true
        echo "ci_credentials failed for $directory. Check debug-ci-credentials-$directory.txt for details."
    fi

    # Check for first secret file
    first_secret_file=$(find "./airbyte-integrations/connectors/$directory/secrets/" -type f | head -n 1)

    if [ -z "$first_secret_file" ]; then
        echo "No secret file found in $directory/secrets."
        if $ci_credentials_failed; then
            if ! airbyte-lib-validate-source --connector-dir "./airbyte-integrations/connectors/$directory/" --validate-install-only > "debug-validate-spec-$directory.txt" 2>&1; then
                failed_ci_credentials+=("$directory")
                echo "validate-source also failed for $directory. Check debug-validate-spec-$directory.txt for details."
            else
                spec_only_succeeded_due_to_no_secrets+=("$directory")
            fi
            rm -rf .venv-source-*
            continue
        fi
    fi

    if [ "$ci_credentials_failed" = false ]; then
        if ! airbyte-lib-validate-source --connector-dir "./airbyte-integrations/connectors/$directory/" --sample-config "$first_secret_file" > "debug-validate-full-$directory.txt" 2>&1; then
            # Retry with --validate-install-only and capture output
            if ! airbyte-lib-validate-source --connector-dir "./airbyte-integrations/connectors/$directory/" --validate-install-only > "debug-validate-spec-$directory.txt" 2>&1; then
                failed_validate_source+=("$directory")
                echo "validate-source failed for $directory. Check debug-validate-full-$directory.txt for details."
            else
                succeeded_spec_only+=("$directory")
            fi
        else
            succeeded+=("$directory")
        fi
    fi

    rm -rf .venv-source-*
done < "$1"

add_remote_registries() {
    local directory="$1"
    local enable="$2"
    local todo_comment="$3"
    local connector_name=$(basename "$directory")

    # Edit metadata.yaml
    local metadata_file="./airbyte-integrations/connectors/$directory/metadata.yaml"
    sed -i '' "/registries:/i \\
  remoteRegistries:\\
    pypi:\\
      enabled: $enable\\
      ${todo_comment}packageName: airbyte-$connector_name\\
" "$metadata_file"
}

# Process succeeded list
for dir in "${succeeded[@]}"; do
    add_remote_registries "$dir" "true" ""
done

# Process succeeded_spec_only_community list
for dir in "${succeeded_spec_only_community[@]}"; do
    add_remote_registries "$dir" "true" ""
done

# Process succeeded_spec_only and spec_only_succeeded_due_to_no_secrets lists
for dir in "${succeeded_spec_only[@]}" "${spec_only_succeeded_due_to_no_secrets[@]}"; do
    # Check if supportLevel is certified
    if grep -q "supportLevel: certified" "./airbyte-integrations/connectors/$dir/metadata.yaml"; then
        add_remote_registries "$dir" "false" "# TODO: Set enabled=true after \`airbyte-lib-validate-source\` is passing.\\
      "
    else
        add_remote_registries "$dir" "true" ""
    fi
done

# Process failed lists
for dir in "${failed_ci_credentials[@]}" "${failed_validate_source[@]}"; do
    add_remote_registries "$dir" "false" "# TODO: Set enabled=true after \`airbyte-lib-validate-source\` is passing.\\
      "
done


# Print results
echo -e "\nSucceeded:"
for dir in "${succeeded[@]}"; do
    echo "$dir"
done

echo -e "\nSucceeded with Spec Only due to full validation failing:"
for dir in "${succeeded_spec_only[@]}"; do
    echo "$dir"
done

echo -e "\nSpec Only Succeeded Due to No Secrets:"
for dir in "${spec_only_succeeded_due_to_no_secrets[@]}"; do
    echo "$dir"
done

echo -e "\nSpec Only Succeeded Due to community connector:"
for dir in "${succeeded_spec_only_community[@]}"; do
    echo "$dir"
done

echo -e "\nFailed ci_credentials:"
for dir in "${failed_ci_credentials[@]}"; do
    echo "$dir"
done

echo -e "\nFailed validate-source:"
for dir in "${failed_validate_source[@]}"; do
    echo "$dir"
done
