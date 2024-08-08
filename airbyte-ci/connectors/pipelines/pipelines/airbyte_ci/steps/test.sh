# List of connector names
connectors=("source-dockerhub" "source-pokeapi" "source-timely")

# Base branch name
base_branch_name="christo/individual-pull-requests"

# Loop through each connector and run the command
for connector in "${connectors[@]}"; do
    # Create a unique branch name for each connector
    branch_name="${base_branch_name}/${connector}"

    # Run the airbyte-ci command with the specific connector and branch name
    airbyte-ci --disable-update-check connectors --name="${connector}" pull-request -m "chore: migrate connector to manifest-only" -b "${branch_name}"
done
