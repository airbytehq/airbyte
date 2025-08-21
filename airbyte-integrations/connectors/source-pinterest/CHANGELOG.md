# Pinterest Source Changelog

## 2.1.9
feat: Migrate report streams to manifest-only pattern - Migrate campaign analytics, advertiser, and ad group report streams from Python to manifest.yaml using AsyncRetriever pattern - Add custom components for report generation, data extraction, and transformation - Simplify source.py to pure YamlDeclarativeSource architecture - Preserve all existing functionality while improving maintainability - Enable easier addition of remaining report streams using established patterns

## 2.1.8
feat: Add support for custom reports configuration

## 2.1.7
feat: Improve error handling for report generation

## 2.1.6
fix: Fix report data parsing and transformation

## 2.1.5
feat: Add support for additional analytics columns

## 2.1.4
fix: Improve rate limiting handling

## 2.1.3
fix: Fix authentication flow for OAuth2

## 2.1.2
feat: Add incremental sync support for analytics streams

## 2.1.1
fix: Fix schema validation for report streams

## 2.1.0
feat: Add support for Pinterest API v5

## 2.0.0
feat: Update state format for incremental streams (breaking change)

## 1.0.0
feat: Initial release with Pinterest API integration (breaking change)
