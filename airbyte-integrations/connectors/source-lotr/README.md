# LOTR API Connector

An Airbyte connector for the Lord of the Rings API using https://lotrapi.co/

## Overview

This connector extracts comprehensive LOTR data from the lotrapi.co API, providing access to books, films, characters, species, races, realms, and groups with rich relational data.

## Features

- **No authentication required** - lotrapi.co is a public API
- **7 comprehensive streams** covering all major LOTR entities
- **Rich relational data** with URL references between entities
- **Cursor pagination support** using links.next URLs for multi-page responses
- **54+ total records** across all streams

## Streams

| Stream | Records | Description |
|--------|---------|-------------|
| books | 4 | Tolkien's books with publication dates and character references |
| films | 6 | Peter Jackson trilogy + extended films with directors/producers |
| characters | 10 | Detailed character data (height, weapons, languages, etc.) |
| species | 6 | Species classifications (Humanoids, Eagles, Tree-Kin, etc.) |
| races | 15 | Races (Hobbits, Dwarves, Elves, etc.) |
| realms | 6 | Geographical realms (The Shire, Arnor, Valinor, etc.) |
| groups | 2 | Character groups (Fellowship, Thorin and Company) |

## API Details

- **Base URL**: https://lotrapi.co/api/v1/
- **Authentication**: None required (public API)
- **Rate Limits**: None observed
- **Response Format**: JSON with `count`, `results`, and `links` fields
- **Pagination**: Cursor-based using `links.next` URLs for multi-page responses

## Sample Data

### Characters
```json
{
  "id": 1,
  "name": "Frodo Baggins",
  "realm": "https://lotrapi.co/api/v1/realms/1",
  "height": "1.06m",
  "hair_color": "Brown",
  "eye_color": "Blue",
  "weapons": ["Sting", "Barrow-blade"],
  "films": ["https://lotrapi.co/api/v1/films/1", "..."]
}
```

### Books
```json
{
  "id": 1,
  "title": "The Fellowship of the Ring",
  "author": "J. R. R. Tolkien",
  "publication_date": "1954-07-29",
  "characters": ["https://lotrapi.co/api/v1/characters/1", "..."]
}
```

## Configuration

No configuration required - the API is completely public.

## Testing Results

- ✅ Manifest validation: PASSED
- ✅ Individual stream tests: 7/7 PASSED
- ✅ Smoke test: 7/7 streams successful, 54 total records
- ✅ Cursor pagination: Fixed to properly follow `links.next` URLs
- ✅ All streams extract data successfully with no errors

## Migration from the-one-api.dev

This connector replaces the previous implementation that used https://the-one-api.dev/v2 which was returning 401 Unauthorized errors. The new lotrapi.co API provides:

- Better reliability and uptime
- No authentication requirements
- Richer data schemas with more detailed character information
- Additional entity types (species, races, realms, groups)
- Proper REST API design with standard pagination

## Development

Built using Airbyte's Connector Builder with declarative YAML manifest approach. Uses cursor pagination to properly handle multi-page API responses by following `links.next` URLs.

### Files
- `lotr_manifest.yaml` - Main connector manifest
- `.env` - Environment configuration (no secrets needed)
- `README.md` - This documentation
