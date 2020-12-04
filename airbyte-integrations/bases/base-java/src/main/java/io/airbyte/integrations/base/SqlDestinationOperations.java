package io.airbyte.integrations.base;

public interface SqlDestinationOperations extends BufferedWriteOperations, InsertTableOperations, TableCreationOperations { }
