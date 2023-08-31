# Connector templates

This directory contains templates used to bootstrap developing new connectors, as well as a generator module which generates code using the templates as input. 

See the `generator/` directory to get started writing a new connector. 
Other directories contain templates used to bootstrap a connector. 

When you do changes here please run `./gradlew :airbyte-integrations:connector-templates:generator:testScaffoldTemplates`
to regenerate the files.