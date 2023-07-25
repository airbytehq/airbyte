package io.airbyte.integrations.source.mongodb;

public enum MongoDbVersions {

    VERSION_4("4.4.23"),
    VERSION_5("5.0.19"),
    VERSION_6("6.0.8");

    private final String version;

    MongoDbVersions(final String version) {
        this.version = version;
    }

    public String getVersion() { return version; }
}
