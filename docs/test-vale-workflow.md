# Test Vale Workflow

This is a test document to verify that the Vale workflow still functons correctly after adding `continue-on-error: true`.

## Purpose

We want to ensure that Vale still runs and detcts spelling errors, but the workflow doesn't fail when it encounters them. This is espeshially important for fork PRs where reviewdog cannot post anotations due to read-only tokens.

## Expected Behavior

- Vale should run and find the spelling errors in this documnt
- The workflow should pass (exit code 0) despite the errors
- This matches the behavior of MarkDownLint which also tolerates errors

## Spelling Errors

This document contains several intentional spelling errors:
- functons (should be "functions")
- detcts (should be "detects")
- espeshially (should be "especially")
- anotations (should be "annotations")
- documnt (should be "document")

These errors should be detected by Vale but should not cause the workflow to fail.
