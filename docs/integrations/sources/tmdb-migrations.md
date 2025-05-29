# TMDb Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 has a schema change.

The search_people schema has been changed it's 'type' in schema['properties']['results']['items']['properties']['known_for']['items']['properties']['poster_path'] to be optionally empty
The search_tv_shows schema has been changed it's pattern in schema['properties']['results']['items']['properties']['overview'] to contain both strings and spaces.