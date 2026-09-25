# Contributing to source-slack-v2

`source-slack-v2` is the Slack source rewritten in Kotlin on the Bulk CDK (`airbyte-cdk/bulk`,
`extract` core, no toolkit). It replaces the manifest-only `source-slack` connector stream for
stream (`users`, `channels`, `channel_members`, `channel_messages`, `threads`) with the same spec,
catalog, records and state envelopes, and reads Slack with far fewer API calls.

## Layout

| Path | What |
|---|---|
| `src/main/kotlin/.../SlackSourceConfigurationSpecification.kt` | The spec (legacy property names), `SlackSpecificationExtender` adds `advanced_auth` |
| `SlackSourceConfiguration.kt` | Validated configuration + factory |
| `SlackApiClient.kt` | HTTP client, per-method adaptive rate limiter, Slack error classification |
| `SlackStreams.kt` | The five streams, their legacy JSON schemas (`src/main/resources/schemas/`) |
| `SlackSharedState.kt` | Per-READ shared state: client, sync start, channel list + join, history page cache |
| `SlackSimpleStreamReader.kt` | `users`, `channels`, `channel_members` |
| `SlackHistoryStreamReader.kt` | `channel_messages` and `threads`: windows, pages, checkpoints, thread call elimination |
| `SlackStreamStateValue.kt` | Legacy-compatible state parsing and emission |
| `src/testFixtures/kotlin/.../FakeSlackServer.kt` | Fake Slack Web API (in-process or standalone) |
| `src/testFixtures/kotlin/.../FakeSlackData.kt` | Deterministic synthetic workspaces |
| `src/test/resources/legacy-spec.json`, `legacy-catalog.json` | Oracles captured from `airbyte/source-slack:3.2.24` |

## Build and test

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)   # JDK 21
./gradlew :airbyte-integrations:connectors:source-slack-v2:compileKotlin
./gradlew :airbyte-integrations:connectors:source-slack-v2:test
CI=true ./gradlew :airbyte-integrations:connectors:source-slack-v2:build   # -Werror + SpotBugs as in CI
./gradlew :airbyte-integrations:connectors:source-slack-v2:assemble        # airbyte/source-slack-v2:dev image
```

No Slack workspace is needed: every test runs against `FakeSlackServer`, started in-process on a
random port and injected through the Micronaut property
`airbyte.connector.extract.slack.api-base-url` (see `SlackTestSupport.withServer`). The tests
also set `airbyte.connector.extract.slack.rate-limit-scale` so that the client's pacing does not
slow them down.

To refresh the spec snapshot after a deliberate spec change, run `SlackSourceSpecTest` once and
copy `build/actual-spec.json` to `src/test/resources/expected-spec.json`; `testLegacySpecParity`
still checks that every legacy property is untouched.

## Running the image against the fake server

```bash
# 1. a fake workspace with 5 channels of 2000 messages, throttled like Slack's Tier 3
./gradlew :airbyte-integrations:connectors:source-slack-v2:runFakeSlack \
    --args="8085 generate:5:2000 --rate-limit conversations.history=50 --rate-limit conversations.replies=50"

# 2. config + catalog in ./secrets (git-ignored)
cat > secrets/fake-config.json <<'JSON'
{"start_date": "2025-07-01T00:00:00Z", "lookback_window": 0, "join_channels": true,
 "credentials": {"option_title": "API Token Credentials", "api_token": "xoxb-fake-token"}}
JSON

# 3. run the image; SLACK_API_BASE_URL points it at the fake
docker run --rm -e SLACK_API_BASE_URL=http://host.docker.internal:8085/api/ \
    -v $PWD/secrets:/secrets airbyte/source-slack-v2:dev check --config /secrets/fake-config.json
docker run --rm -e SLACK_API_BASE_URL=http://host.docker.internal:8085/api/ \
    -v $PWD/secrets:/secrets airbyte/source-slack-v2:dev discover --config /secrets/fake-config.json
```

`FakeSlackServer` also accepts `--non-marketplace` (15 messages per page, the regime Slack applies
to unlisted apps) and a JSON workspace file instead of `generate:<channels>:<messages>`
(`FakeSlackWorkspace.load`; `toJson()` writes one).

## Against a real workspace

Put a config with a bot token (`xoxb-`, scopes `channels:history`, `channels:join`,
`channels:read`, `groups:read`, `groups:history`, `users:read`) in `secrets/config.json` and run
the image without `SLACK_API_BASE_URL`. Watch the log for `Slack API rate limited` lines: the
client paces each method at its documented tier and adapts to 429s, so they should be rare.

## Formatting

Connector projects have no `spotlessApply`; format with the ktfmt version pinned in
`spotless-maven-pom.xml`:

```bash
curl -sSfL -o /tmp/ktfmt.jar https://repo1.maven.org/maven2/com/facebook/ktfmt/0.39/ktfmt-0.39-jar-with-dependencies.jar
find airbyte-integrations/connectors/source-slack-v2/src -name '*.kt' | xargs java -jar /tmp/ktfmt.jar --kotlinlang-style
```
