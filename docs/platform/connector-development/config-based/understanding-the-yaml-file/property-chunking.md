# Property Chunking

Property chunking enables connectors to handle APIs with limitations on the number of properties that can be fetched per request. This feature breaks down large property lists into smaller, manageable chunks and merges the results back into complete records.

Many critical connectors require this functionality to work with APIs that have property limits, such as HubSpot (character limits) and LinkedIn Ads (property count limits).

## Overview

Property chunking works by:
1. Fetching the complete list of properties (either statically defined or dynamically from an API endpoint)
2. Splitting properties into chunks based on configured limits
3. Making separate API requests for each chunk
4. Merging the results back into complete records using a merge strategy

## Schema

```yaml
QueryProperties:
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

### PropertyChunking

```yaml
PropertyChunking:
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
      description: Dictates how records that require multiple requests to get all properties should be emitted to the destination
      "$ref": "#/definitions/GroupByKeyMergeStrategy"
    $parameters:
      type: object
      additionalProperties: true
```

### PropertiesFromEndpoint

```yaml
PropertiesFromEndpoint:
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
    retriever:
      description: Requester component that describes how to fetch the properties to query from a remote API endpoint.
      anyOf:
        - "$ref": "#/definitions/CustomRetriever"
        - "$ref": "#/definitions/SimpleRetriever"
    $parameters:
      type: object
      additionalProperties: true
```

### GroupByKeyMergeStrategy

```yaml
GroupByKeyMergeStrategy:
  type: object
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
      examples:
        - "id"
        - ["parent_id", "end_date"]
```

## Property Limit Types

### Characters
When using `characters` as the limit type, the total character count of all property names (including delimiters) is used to determine chunk size.

### Property Count
When using `property_count` as the limit type, the number of individual properties is used to determine chunk size.

## Usage Examples

### HubSpot: Character-based Chunking

HubSpot's API has a limit on the total character count of properties that can be requested. Here's how to configure character-based chunking:

```yaml
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
          path: "/properties/v2/{{ stream_name }}/properties"
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

### LinkedIn Ads: Property Count Chunking

LinkedIn Ads API limits the number of properties that can be requested per call. Here's how to configure property count-based chunking:

```yaml
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

## Record Merging

When multiple requests are needed to fetch all properties for a record, the results must be merged back together. The `GroupByKeyMergeStrategy` combines records based on a specified key field.

### Simple Key Merging
For records with a single unique identifier:

```yaml
record_merge_strategy:
  type: GroupByKeyMergeStrategy
  key: "id"
```

### Compound Key Merging
For records requiring multiple fields to create a unique identifier:

```yaml
record_merge_strategy:
  type: GroupByKeyMergeStrategy
  key: ["parent_id", "end_date"]
```

## Always Include Properties

Some properties must be included in every chunk request, typically because they're needed for record merging or API requirements:

```yaml
always_include_properties:
  - dateRange
  - pivotValues
```

These properties are automatically added to each chunk and don't count toward the property limit.
