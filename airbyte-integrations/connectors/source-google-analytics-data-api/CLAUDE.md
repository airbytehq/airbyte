# source-google-analytics-data-api

## Important
This is **Google Analytics 4 (GA4)** (`source-google-analytics-data-api`), NOT the deprecated Universal Analytics (`source-google-analytics-v4`). All work goes here.

## Unique Behaviors
See [BEHAVIOR.md](./BEHAVIOR.md) for documented unique behaviors:
1. Positional key-value array extraction (headers and values returned separately)
2. Two-level Jinja interpolation in component mappings (`{% raw %}` for runtime vs template-level)
3. Fully dynamic stream construction from config (12+ ComponentMappingDefinitions, no static streams)
4. DimensionFilter config transformation (config schema differs from API request schema)
5. Cohort reports disable date ranges and incremental sync
6. Rate limit quota cannot be self-service increased — requires DoIT escalation (via Ralph or Davin)
