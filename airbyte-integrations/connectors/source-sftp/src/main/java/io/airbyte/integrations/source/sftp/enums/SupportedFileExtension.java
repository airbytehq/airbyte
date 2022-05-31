package io.airbyte.integrations.source.sftp.enums;

public enum SupportedFileExtension {
    CSV("csv"),
    JSON("json");

    public final String typeName;

    SupportedFileExtension(String typeName) {
        this.typeName = typeName;
    }
}
