# Slack Incremental Dependency Test Source

**Purpose**: Minimal test connector to reproduce GitHub issue [#50962](https://github.com/airbytehq/airbyte/issues/50962) - `incremental_dependency: true` not working on Airbyte Cloud.

## The Problem

`SubstreamPartitionRouter` with `incremental_dependency: true` works correctly on **Airbyte OSS** but fails on **Airbyte Cloud**.

### Expected Behavior (OSS)
On incremental sync:
1. `channel_messages` stream fetches only NEW messages since last sync ✓
2. `threads` stream fetches replies only for those NEW messages (thanks to `incremental_dependency: true`) ✓
3. Efficient: Only processes new data ✓

### Actual Behavior (Cloud)
On incremental sync:
1. `channel_messages` stream fetches only NEW messages ✓
2. `threads` stream fetches replies for ALL messages (old + new) ✗
3. Inefficient: Full refresh of child stream every sync ✗

## Streams

### 1. channels
- Lists Slack channels
- Needed to provide channel IDs to other streams

### 2. channel_messages (Parent)
- Messages posted in Slack channels
- **Incremental** by timestamp (`float_ts`)
- On incremental sync: only fetches messages since last sync

### 3. threads (Child)
- Replies to channel messages (threaded conversations)
- Uses `SubstreamPartitionRouter` with **`incremental_dependency: true`**
- **Should** only fetch replies for new messages
- **Actually** fetches replies for ALL messages on Cloud (bug)

## Configuration

```json
{
  "api_token": "xoxb-your-slack-token",
  "start_date": "2024-01-01T00:00:00Z"
}
```

### Getting a Slack API Token

1. Go to https://api.slack.com/apps
2. Create a new app or use existing
3. Add Bot Token Scopes:
   - `channels:read`
   - `channels:history`
4. Install app to workspace
5. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

## Testing Locally (OSS Behavior)

```bash
# 1. Create config
cat > secrets/config.json <<EOF
{
  "api_token": "xoxb-your-token",
  "start_date": "2024-01-01T00:00:00Z"
}
EOF

# 2. Test with Docker
docker run --rm \
  -v $(pwd):/data \
  -v $(pwd)/secrets/config.json:/config.json \
  airbyte/source-declarative-manifest:5.17.0 \
  discover --config /config.json

# 3. First sync (full refresh)
docker run --rm \
  -v $(pwd):/data \
  -v $(pwd)/secrets/config.json:/config.json \
  -v /tmp/catalog.json:/catalog.json \
  airbyte/source-declarative-manifest:5.17.0 \
  read --config /config.json --catalog /catalog.json \
  > /tmp/sync1.jsonl

# 4. Extract state
grep '"type":"STATE"' /tmp/sync1.jsonl | tail -1 > /tmp/state.json

# 5. Second sync (incremental)
# On OSS: threads should only process NEW messages
# On Cloud: threads will process ALL messages (bug)
docker run --rm \
  -v $(pwd):/data \
  -v $(pwd)/secrets/config.json:/config.json \
  -v /tmp/catalog.json:/catalog.json \
  -v /tmp/state.json:/state.json \
  airbyte/source-declarative-manifest:5.17.0 \
  read --config /config.json --catalog /catalog.json --state /state.json \
  > /tmp/sync2.jsonl
```

## Verification

To verify `incremental_dependency` works correctly:

1. **First sync**: Note the number of messages and threads fetched
2. **Post a NEW message** in one of your Slack channels (with a thread reply)
3. **Second sync**:
   - ✅ OSS: `threads` stream should only fetch the thread for the 1 new message
   - ❌ Cloud: `threads` stream will fetch threads for ALL messages again

## Deployment to Cloud

1. Build the connector:
   ```bash
   cd ~/airbyte
   airbyte-ci connectors --name source-slack-incremental-test build
   ```

2. Upload to Airbyte Cloud:
   - Go to Settings > Sources
   - Click "New connector" > "Custom connector"
   - Upload the Docker image

3. Create a source and connection

4. Run incremental syncs and observe the bug

## Related Issues

- GitHub Issue: https://github.com/airbytehq/airbyte/issues/50962
- Support Ticket: #16561
- Affects production connectors:
  - `source-slack` (threads stream)
  - Custom Gong connector (call transcripts)
  - Custom Fathom connector (recording transcripts)

## Key Manifest Section

```yaml
threads:
  retriever:
    partition_router:
      type: SubstreamPartitionRouter
      parent_stream_configs:
        - type: ParentStreamConfig
          stream:
            $ref: "#/definitions/streams/channel_messages"
          # This is the feature being tested:
          incremental_dependency: true  # <-- Works on OSS, broken on Cloud
          parent_key: ts
          partition_field: float_ts
```

The root cause is that Airbyte Cloud does not pass the parent stream's state to `input_state.json`, causing the child stream to iterate over all parent records instead of only new ones.
