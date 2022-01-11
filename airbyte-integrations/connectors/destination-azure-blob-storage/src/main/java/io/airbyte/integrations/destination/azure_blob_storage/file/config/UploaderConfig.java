package io.airbyte.integrations.destination.azure_blob_storage.file.config;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.azure_blob_storage.file.UploaderType;
import io.airbyte.integrations.destination.azure_blob_storage.file.UploadingMethod;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import lombok.Builder;
import lombok.Getter;

import java.util.Map;

@Builder
@Getter
public class UploaderConfig {

    private JsonNode stagingConfig;
    private UploaderType uploaderType;
    private boolean newlyCreatedBlob;
    private boolean keepFilesInStorage;
    private UploadingMethod uploadingMethod;
    private AppendBlobClient appendBlobClient;
    private ConfiguredAirbyteStream configStream;
}
