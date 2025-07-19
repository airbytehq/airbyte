# Property chunking

Property chunking enables connectors to handle APIs with limitations on the number of properties that you can fetch per request. This feature breaks down large property lists into smaller, manageable chunks and merges the results back into complete records. Some connectors require this capability to work with APIs that have property limits.

## Overview

Property chunking works in these steps.

1. Fetching the complete list of properties (either statically defined or dynamically from an API endpoint)

2. Splitting properties into chunks based on configured limits

3. Making separate API requests for each chunk

4. Merging the results back into complete records using a merge strategy, like combining sets of property values into a single record according to their primary key ID

## Schema

```yaml
QueryProperties:
  title: Query Properties
  description: For APIs that require explicit specification of the properties to query for, this component specifies which property fields and how they are supplied to outbound requests.
  type: object
  required:
    - type
    - property_list
  properties:
    type:
      type: string
      enum: [QueryProperties]
    property_list:
      title: Property List
      description: The set of properties that will be queried for in the outbound request. This can either be statically defined or dynamic based on an API endpoint
      anyOf:
        - type: array
          items:
            type: string
        - "$ref": "#/definitions/PropertiesFromEndpoint"
    always_include_properties:
      title: Always Include Properties
      description: The list of properties that should be included in every set of properties when multiple chunks of properties are being requested.
      type: array
      items:
        type: string
    property_chunking:
      title: Property Chunking
      description: Defines how query properties will be grouped into smaller sets for APIs with limitations on the number of properties fetched per API request.
      "$ref": "#/definitions/PropertyChunking"
    $parameters:
      type: object
      additionalProperties: true
```

### `PropertyChunking`

```yaml
PropertyChunking:
  title: Property Chunking
  description: For APIs with restrictions on the amount of properties that can be requester per request, property chunking can be applied to make multiple requests with a subset of the properties.
  type: object
  required:
    - type
    - property_limit_type
  properties:
    type:
      type: string
      enum: [PropertyChunking]
    property_limit_type:
      title: Property Limit Type
      description: The type used to determine the maximum number of properties per chunk
      enum:
        - characters
        - property_count
    property_limit:
      title: Property Limit
      description: The maximum amount of properties that can be retrieved per request according to the limit type.
      type: integer
    record_merge_strategy:
      title: Record Merge Strategy
      description: Dictates how to records that require multiple requests to get all properties should be emitted to the destination
      "$ref": "#/definitions/GroupByKeyMergeStrategy"
    $parameters:
      type: object
      additionalProperties: true
```

### `PropertiesFromEndpoint`

```yaml
PropertiesFromEndpoint:
  title: Properties from Endpoint
  description: Defines the behavior for fetching the list of properties from an API that will be loaded into the requests to extract records.
  type: object
  required:
    - type
    - property_field_path
    - retriever
  properties:
    type:
      type: string
      enum: [PropertiesFromEndpoint]
    property_field_path:
      description: Describes the path to the field that should be extracted
      type: array
      items:
        type: string
      examples:
        - ["name"]
      interpolation_context:
        - config
        - parameters
    retriever:
      description: Requester component that describes how to fetch the properties to query from a remote API endpoint.
      anyOf:
        - "$ref": "#/definitions/SimpleRetriever"
        - "$ref": "#/definitions/CustomRetriever"
    $parameters:
      type: object
      additionalProperties: true
```

### `GroupByKeyMergeStrategy`

```yaml
GroupByKeyMergeStrategy:
  title: Group by Key
  description: Record merge strategy that combines records according to fields on the record.
  required:
    - type
    - key
  properties:
    type:
      type: string
      enum: [GroupByKeyMergeStrategy]
    key:
      title: Key
      description: The name of the field on the record whose value will be used to group properties that were retrieved through multiple API requests.
      anyOf:
        - type: string
        - type: array
          items:
            type: string
      examples:
        - "id"
        - ["parent_id", "end_date"]
    $parameters:
      type: object
      additionalProperties: true
```

## Property limit types

### Characters

When using `characters` as the limit type, the total character count of all property names (including delimiters) determines chunk size.

### Property count

When using `property_count` as the limit type, the number of individual properties determines chunk size.

## Record merging

When the connector needs multiple requests to fetch all properties for a record, it must merge the results back together. The `GroupByKeyMergeStrategy` combines records based on a specified key field.

### Simple key merging

For records with a single unique identifier.

```yaml title="manifest.yaml"
record_merge_strategy:
  type: GroupByKeyMergeStrategy
  key: "id"
```

### Compound key merging

For records requiring multiple fields to create a unique identifier.

```yaml title="manifest.yaml"
record_merge_strategy:
  type: GroupByKeyMergeStrategy
  key: ["parent_id", "end_date"]
```

## Always include properties

Some properties must be in every chunk request, typically because they're needed for record merging or API requirements. These properties are automatically added to each chunk and don't count toward the property limit.

```yaml title="manifest.yaml"
always_include_properties:
  - dateRange
  - pivotValues
```

## Usage examples

Here are examples of how Airbyte has used property chunking in some connectors.

### HubSpot: fetching properties from an API endpoint with character-based chunking

Airbyte's HubSpot connector uses dynamic property chunking. Instead of specifying a static list of properties, it makes a request to `https://api.hubapi.com/properties/v2/contacts/properties` to determine the list of properties.

```yaml title="manifest.yaml"
request_parameters:
  properties:
    type: QueryProperties
    property_list:
      type: PropertiesFromEndpoint
      property_field_path: ["name"]
      retriever:
        type: SimpleRetriever
        requester:
          type: HttpRequester
          url_base: "https://api.hubapi.com"
          path: "/properties/v2/contacts/properties"
          http_method: "GET"
        record_selector:
          type: RecordSelector
          extractor:
            type: DpathExtractor
            field_path: []
    property_chunking:
      type: PropertyChunking
      property_limit_type: characters
      property_limit: 15000
```

### LinkedIn Ads: Property count chunking

LinkedIn Ads' API limits the number of properties you can request per call. Airbyte's connector provides a static list of properties and makes a series of requests that always includes `dateRange` and `pivotValues`, then merges responses into a single record using the end date and the pivot values.

```yaml title="manifest.yaml"
request_parameters:
  fields:
    type: QueryProperties
    property_list:
      - actionClicks
      - adUnitClicks
      - approximateUniqueImpressions
      - cardClicks
      - cardImpressions
      - clicks
      - commentLikes
      - comments
      - companyPageClicks
      - conversionValueInLocalCurrency
      - costInLocalCurrency
      - costInUsd
      - externalWebsiteConversions
      - externalWebsitePostClickConversions
      - externalWebsitePostViewConversions
      - follows
      - fullScreenPlays
      - impressions
      - landingPageClicks
      - leadGenerationEmailClicks
      - leadGenerationEmailOpens
      - likes
      - oneClickLeadFormOpens
      - oneClickLeads
      - opens
      - otherEngagements
      - reactions
      - sends
      - shares
      - textUrlClicks
      - totalEngagements
      - videoCompletions
      - videoFirstQuartileCompletions
      - videoMidpointCompletions
      - videoStarts
      - videoThirdQuartileCompletions
      - videoViews
      - viralCardClicks
      - viralCardImpressions
      - viralClicks
      - viralCommentLikes
      - viralComments
      - viralCompanyPageClicks
      - viralExternalWebsiteConversions
      - viralExternalWebsitePostClickConversions
      - viralExternalWebsitePostViewConversions
      - viralFollows
      - viralFullScreenPlays
      - viralImpressions
      - viralLandingPageClicks
      - viralLikes
      - viralOneClickLeadFormOpens
      - viralOtherEngagements
      - viralReactions
      - viralShares
      - viralTotalEngagements
      - viralVideoCompletions
      - viralVideoFirstQuartileCompletions
      - viralVideoMidpointCompletions
      - viralVideoStarts
      - viralVideoThirdQuartileCompletions
      - viralVideoViews
    always_include_properties:
      - dateRange
      - pivotValues
    property_chunking:
      type: PropertyChunking
      property_limit_type: property_count
      property_limit: 18
      record_merge_strategy:
        type: GroupByKeyMergeStrategy
        key: ["end_date", "string_of_pivot_values"]
```
