# Changelog

## 6.0.0 - 2025-10-23

### Breaking Changes
- Changed `CIContext.MASTER` enum value from `"master"` to `"main"` to reflect repository default branch rename
- Changed default `--diffed-branch` parameter from `"master"` to `"main"`
- Updated GitHub URL references to use `main` branch instead of `master`
- Updated all comments and error messages referencing `master` branch to use `main`

### Migration Guide
If you have code that depends on the `CIContext.MASTER` enum value or the default `--diffed-branch` parameter:
- Update any code checking for `CIContext.MASTER == "master"` to check for `"main"` instead
- Update any explicit `--diffed-branch=master` arguments to use `--diffed-branch=main`
- Update any GitHub URLs referencing `/master/` to use `/main/`

## 5.5.0 and earlier
See git history for previous changes.
