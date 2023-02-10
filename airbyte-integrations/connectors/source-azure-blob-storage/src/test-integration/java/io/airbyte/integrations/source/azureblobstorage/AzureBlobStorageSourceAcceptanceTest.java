package io.airbyte.integrations.source.azureblobstorage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

public class AzureBlobStorageSourceAcceptanceTest extends SourceAcceptanceTest {

    @Override
    protected String getImageName() {
        return null;
    }

    @Override
    protected JsonNode getConfig() throws Exception {
        return null;
    }

    @Override
    protected void setupEnvironment(TestDestinationEnv environment) throws Exception {

    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) throws Exception {

    }

    @Override
    protected ConnectorSpecification getSpec() throws Exception {
        return null;
    }

    @Override
    protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
        return null;
    }

    @Override
    protected JsonNode getState() throws Exception {
        return null;
    }
}
