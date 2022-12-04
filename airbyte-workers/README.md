# airbyte-workers

This module contains the logic for how Jobs are executed. Jobs are executed using a tool called Temporal.

## Temporal Development

### Versioning

Temporal is maintaining an internal history of the activity it runs. This history is based on a specific order. If we restart a temporal workflow with
a new implementation that has a different order, the workflow will be stuck and will need manual action to be properly restarted. Temporal provides
an API to be able to manage those changes smoothly. However, temporal is very permissive with version rules. Airbyte will follow
the following rules:

- There will be one global version per workflow, meaning that we will use a single tag per workflow.
- All the following code modifications will need to bump the version number, it won't be limited to a release of a new airbyte version
    - Addition of an activity
    - Deletion of an activity
    - Change of the input of an activity
    - Addition of a temporal sleep timer

The way to use this version should be the following:

If no prior version usage is present:

```
final int version = Workflow.getVersion(VERSION_LABEL, MINIMAL_VERSION, CURRENT_VERSION);

if (version >= CURRENT_VERSION) {
        // New implemenation
}
```

if some prior version usage is present (we bump the version from 4 to 5 in this example):

```
final int version = Workflow.getVersion(VERSION_LABEL, MINIMAL_VERSION, CURRENT_VERSION);

if (version <= 4 && version >= MINIMAL_VERSION) {
        // old implemenation
} else if (version >= CURRENT_VERSION) {
        // New implemenation
}
```

### Removing a version

Removing a version is a potential breaking change and should be done version carefully. We should maintain a MINIMAL_VERSION to keep track of the
current minimal version. Both MINIMAL_VERSION and CURRENT_VERSION needs to be present on the workflow file even if they are unused (if they have been
used once).
