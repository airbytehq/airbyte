# airbyte-bootloader

This application runs at start up for Airbyte. It is responsible for making sure that the environment is upgraded and in a good state. e.g. It makes sure the database has been migrated to the correct version.

## Entrypoint
* BootloaderApp.java - has the main method for running the bootloader.
