# 🐛 Build Debugging Guide

This guide explains how to use the detailed timing information to identify where the build is hanging.

## Quick Start

### Run with Debug Timing

```bash
cd docusaurus

# For development build with detailed timing
pnpm run start:debug

# For production build with detailed timing
pnpm run build:debug
```

Both commands will:
1. Show detailed timing for each build stage
2. Save all output to `build-timing.log`
3. Display timing in console in real-time

## What Gets Timed

### prepare-public-api script logs:

```
⏱️  [START] Prepare public API spec
FETCH_SPECS: 2.5s          ← Fetching OpenAPI specs from URLs
MERGE_SPECS: 0.3s          ← Merging all 17 YAML files
INJECT_TAGS: 0.1s          ← Adding metadata tags
VALIDATE_SPEC: 1.2s        ← Validating OpenAPI spec structure
EXTRACT_SCHEMAS: 5.8s      ← Processing 64 source configurations
   📊 Extracted 64 source configurations
SAVE_JSON: 0.4s            ← Writing source-configs-dereferenced.json
   📦 JSON file size: 631.42 KB
DUMP_YAML: 3.2s            ← Converting spec to YAML format
WRITE_YAML: 1.1s           ← Writing YAML file
   📦 YAML file size: 3.45 MB
⏱️  [COMPLETE] Prepare public API spec
TOTAL: 14.6s               ← Total time for this step
```

### Webpack build logs:

```
● Client 20% building /Users/letiescanciano/Airbyte/airbyte/
● Server 18% building /Users/letiescanciano/Airbyte/airbyte/
[waiting for progress...]
```

During webpack build, if it gets stuck, you can see:
- Client/Server progress percentages
- How long it's been in each stage
- Whether it's actually progressing or truly hung

## Expected Timings (Reference)

On a MacBook Pro with 32GB RAM and 8GB allocation:

| Stage | Expected Time | If Hanging |
|-------|---|---|
| FETCH_SPECS | 2-5s | > 10s |
| MERGE_SPECS | 0.2-0.5s | > 2s |
| VALIDATE_SPEC | 0.5-2s | > 5s |
| EXTRACT_SCHEMAS | 2-8s | > 15s |
| DUMP_YAML | 1-4s | > 8s |
| Webpack build | 30-60s | > 120s |

## Analyzing the Log File

After running, check `build-timing.log`:

```bash
# View just the timing summary
grep "⏱️\|TOTAL\|📊\|📦" build-timing.log

# View all output with line numbers
cat -n build-timing.log

# Find warnings or errors
grep "⚠️\|❌" build-timing.log

# Track memory usage patterns
grep "memory\|heap" build-timing.log
```

## Common Hang Scenarios

### Scenario 1: Stuck on EXTRACT_SCHEMAS
```
EXTRACT_SCHEMAS: [takes > 15 seconds]
```
**Diagnosis**: Schema dereferencing is slow
**Solution**: Check if schemas have circular references

### Scenario 2: Stuck on Webpack
```
● Client 20% building...
[no progress for > 60s]
```
**Diagnosis**: Webpack is building but very slowly
**Solution**: Check memory usage with `top` or `htop`

### Scenario 3: Stuck on FETCH_SPECS
```
FETCH_SPECS: [takes > 30 seconds]
```
**Diagnosis**: Network issue or large spec file
**Solution**: Check internet connection or skip fetch with cached version

## Real-Time Monitoring

While build is running, in another terminal:

```bash
# Monitor memory usage
top -p $(pgrep -f "node.*docusaurus")

# Monitor file I/O
lsof -p $(pgrep -f "node.*docusaurus")

# Watch log file in real-time
tail -f build-timing.log
```

## Next Steps

1. Run `pnpm run start:debug` or `pnpm run build:debug`
2. Wait for build to complete (or hang)
3. Check `build-timing.log` for timing breakdown
4. Report which stage is taking the longest:
   - Fetching?
   - Schema processing?
   - Webpack bundling?
5. Share the relevant section of `build-timing.log` for further investigation

---

**Note**: The timing information is added via `console.time()` and `console.timeEnd()` calls in the build scripts, so you see real-time output and can identify bottlenecks immediately.
