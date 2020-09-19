### Upgrading an Integration
1. Make sure you can build the integration locally

    ```
    ./tools/integrations/manage.sh build <path to integration>
    # e.g.
    # ./tools/integrations/manage.sh build airbyte-integrations/singer/postgres/source
    ```
1. Update the version in the dockerfile of the integration `LABEL io.airbyte.version=0.1.0`
1. (If you want Dataline to use this new integration) Update the version of the integration in `Integrations.java`
1. Publish it to docker hub. `./tools/integrations/manage.sh build <path to integration>`
1. Merge you changes. (Make sure you've done the previous step first, otherwise the application will look for the wrong integration!!!)
