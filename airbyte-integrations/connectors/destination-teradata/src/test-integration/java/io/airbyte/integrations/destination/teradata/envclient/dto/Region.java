package io.airbyte.integrations.destination.teradata.envclient.dto;


public enum Region {

    US_CENTRAL("us-central"),

    US_EAST("us-east"),

    US_WEST("us-west"),

    SOUTHAMERICA_EAST("southamerica-east"),

    EUROPE_WEST("europe-west"),

    ASIA_SOUTH("asia-south"),

    ASIA_NORTHEAST("asia-northeast"),

    ASIA_SOUTHEAST("asia-southeast"),

    AUSTRALIA_SOUTHEAST("australia-southeast");


    private final String regionName;

    Region(String regionName) {
        this.regionName = regionName;
    }

    public String getRegionName() {
        return regionName;
    }
}
