/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Separate mixin for GCS region. This is separate from [GcsCommonConfiguration] because some
 * destinations know the GCS region from a different part of their spec. For example, Bigquery
 * already asks the user for the Bigquery region, which determines the GCS region - so in Bigquery,
 * we only need the [GcsCommonConfiguration], and don't need to use this mixin.
 */
interface GcsRegionSpecification {
    @get:JsonSchemaTitle("GCS Bucket Region")
    @get:JsonPropertyDescription(
        """Select a Region of the GCS Bucket. Read more <a href="https://cloud.google.com/storage/docs/locations">here</a>."""
    )
    @get:JsonProperty("gcs_bucket_region", defaultValue = "us")
    val gcsBucketRegion: GcsRegion?
}

// see https://cloud.google.com/storage/docs/locations#available-locations
enum class GcsRegion(@get:JsonValue val region: String) {
    // multi-regions
    ASIA("asia"),
    EU("eu"),
    US("us"),

    // preferred dual-regions
    ASIA1("asia1"),
    EUR4("eur4"),
    EUR5("eur5"),
    EUR7("eur7"),
    EUR8("eur8"),
    NAM4("nam4"),

    // regions
    AFRICA_SOUTH1("africa-south1"),
    ASIA_EAST1("asia-east1"),
    ASIA_EAST2("asia-east2"),
    ASIA_NORTHEAST1("asia-northeast1"),
    ASIA_NORTHEAST2("asia-northeast2"),
    ASIA_NORTHEAST3("asia-northeast3"),
    ASIA_SOUTH1("asia-south1"),
    ASIA_SOUTH2("asia-south2"),
    ASIA_SOUTHEAST1("asia-southeast1"),
    ASIA_SOUTHEAST2("asia-southeast2"),
    AUSTRALIA_SOUTHEAST1("australia-southeast1"),
    AUSTRALIA_SOUTHEAST2("australia-southeast2"),
    EUROPE_CENTRAL2("europe-central2"),
    EUROPE_NORTH1("europe-north1"),
    EUROPE_NORTH2("europe-north2"),
    EUROPE_SOUTHWEST1("europe-southwest1"),
    EUROPE_WEST1("europe-west1"),
    EUROPE_WEST2("europe-west2"),
    EUROPE_WEST3("europe-west3"),
    EUROPE_WEST4("europe-west4"),
    EUROPE_WEST6("europe-west6"),
    EUROPE_WEST8("europe-west8"),
    EUROPE_WEST9("europe-west9"),
    EUROPE_WEST10("europe-west10"),
    EUROPE_WEST12("europe-west12"),
    ME_CENTRAL1("me-central1"),
    ME_CENTRAL2("me-central2"),
    ME_WEST1("me-west1"),
    NORTHAMERICA_NORTHEAST1("northamerica-northeast1"),
    NORTHAMERICA_NORTHEAST2("northamerica-northeast2"),
    NORTHAMERICA_SOUTH1("northamerica-south1"),
    SOUTHAMERICA_EAST1("southamerica-east1"),
    SOUTHAMERICA_WEST1("southamerica-west1"),
    US_CENTRAL1("us-central1"),
    US_EAST1("us-east1"),
    US_EAST4("us-east4"),
    US_EAST5("us-east5"),
    US_SOUTH1("us-south1"),
    US_WEST1("us-west1"),
    US_WEST2("us-west2"),
    US_WEST3("us-west3"),
    US_WEST4("us-west4"),
}
