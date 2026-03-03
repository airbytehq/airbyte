# Incremental Dependency Test Source

**Purpose**: Minimal test connector to reproduce [GitHub issue #50962](https://github.com/airbytehq/airbyte/issues/50962) - `incremental_dependency: true` not working on Airbyte Cloud.

## The Problem

`SubstreamPartitionRouter` with `incremental_dependency: true` works correctly on **Airbyte OSS** but fails on **Airbyte Cloud**.

### Expected Behavior (OSS)
On incremental sync:
1. `posts` stream fetches only NEW posts since last sync ✓
2. `comments` stream fetches comments only for those NEW posts (thanks to `incremental_dependency: true`) ✓
3. Efficient: Only processes new data ✓

### Actual Behavior (Cloud)
On incremental sync:
1. `posts` stream fetches only NEW posts ✓
2. `comments` stream fetches comments for ALL posts (old + new) ✗
3. Inefficient: Full refresh of child stream every sync ✗

## Streams

### 1. posts (Parent)
- Blog posts from JSONPlaceholder API
- **Incremental** by ID
- On incremental sync: only fetches posts with ID > last synced ID

### 2. comments (Child)
- Comments on blog posts
- Uses `SubstreamPartitionRouter` with **`incremental_dependency: true`**
- **Should** only fetch comments for new posts
- **Actually** fetches comments for ALL posts on Cloud (bug)

## Why JSONPlaceholder?

✅ **No authentication** - Anyone can test instantly
✅ **Free & public** - No account setup needed
✅ **Simple** - Clear parent/child relationship (posts → comments)
✅ **Easy for reviewers** - Can test in seconds

## Configuration

```json
{
  "start_date": "2020-01-01"
}
```

No API keys needed!

## Testing Locally (OSS Behavior)

```bash
# 1. Test discover
docker run --rm \
  -v $(pwd):/data \
  airbyte/source-declarative-manifest:5.17.0 \
  discover --config /data/secrets/config.json

# 2. First sync (full refresh baseline)
docker run --rm \
  -v $(pwd):/data \
  airbyte/source-declarative-manifest:5.17.0 \
  read --config /data/secrets/config.json --catalog /data/catalog.json \
  > /tmp/sync1.jsonl

# 3. Extract state
grep '"type":"STATE"' /tmp/sync1.jsonl | tail -1 > /tmp/state.json

# 4. Second sync (incremental)
# On OSS: comments should only process NEW posts
# On Cloud: comments will process ALL posts (bug)
docker run --rm \
  -v $(pwd):/data \
  -v /tmp/state.json:/state.json \
  airbyte/source-declarative-manifest:5.17.0 \
  read --config /data/secrets/config.json --catalog /data/catalog.json --state /state.json \
  > /tmp/sync2.jsonl
```

## Verification

JSONPlaceholder has ~100 posts total. Each post has ~5 comments.

**First sync**: Fetches all 100 posts + ~500 comments
**Second sync** (no new data):
- ✅ OSS: posts = 0, comments = 0 (nothing new)
- ❌ Cloud: posts = 0, comments = ~500 (fetches all again, proving the bug)

## Deployment to Cloud

1. Upload connector to Airbyte Cloud as custom connector
2. Create source with config `{"start_date": "2020-01-01"}`
3. Create connection with both streams
4. Run first sync (baseline)
5. Run second sync immediately - observe comments full refresh

## Related Issues

- GitHub Issue: https://github.com/airbytehq/airbyte/issues/50962
- Support Ticket: #16561
- Also affects: `source-slack` (threads), custom Gong/Fathom connectors

## Key Manifest Section

```yaml
comments:
  partition_router:
    type: SubstreamPartitionRouter
    parent_stream_configs:
      - type: ParentStreamConfig
        stream: posts
        incremental_dependency: true  # <-- Works on OSS, broken on Cloud
        parent_key: id
        partition_field: post_id
```

The root cause is that Airbyte Cloud does not pass the parent stream's state to `input_state.json`, causing the child stream to iterate over all parent records instead of only new ones.
