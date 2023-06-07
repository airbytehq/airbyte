**Connector Nightly Report**

CONNECTORS:   total: {{ total_connectors }}

Sources:      total: {{ source_stats["total"] }} / tested: {{ source_stats["tested"] }} / success: {{ source_stats["success"] }} ({{ source_stats["success_percent"] }}%)

Destinations: total: {{ destination_stats["total"] }} / tested: {{ destination_stats["tested"] }} / success: {{ destination_stats["success"] }} ({{ destination_stats["success_percent"] }}%)

**FAILED LAST BUILD ONLY  - {{ failed_last_build_only_count }} connectors:**

{{ failed_last_build_only }}


**FAILED TWO LAST BUILDS - {{ failed_last_build_two_builds_count }} connectors:**

{{ failed_last_build_two_builds }}
