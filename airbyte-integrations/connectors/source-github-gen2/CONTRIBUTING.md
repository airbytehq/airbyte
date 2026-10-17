# Contributing to source-github-gen2

This connector is a clean-slate rewrite of `source-github`. It is intentionally
**not** backwards compatible: stream names, field names and field types differ, and
no migration path from Gen-1 is provided.

For general connector development and testing instructions, see
[Building a connector](https://docs.airbyte.com/connector-development/) and the
connector's [README](./README.md). This document covers only what is specific to this
connector: the design rules it is held to.

The rules below are the criteria used to decide what the connector keeps, drops or
reshapes from a GitHub API response. Read them before adding a stream or a field —
they are the reason most reviews on this connector go the way they do.

## 1. Manifest-only, no custom Python

Everything is expressed in `manifest.yaml` with declarative components
(`DpathExtractor`, `AddFields`, `RemoveFields`, `SubstreamPartitionRouter`,
`DatetimeBasedCursor`). A custom component is only acceptable if the behavior
provably cannot be expressed declaratively; the fix of first resort is a CDK
feature request, not a Python file here.

## 2. Normalize; do not inline another entity's mutable state

GitHub embeds whole entities inside child records: every issue carries a full `user`
object, every workflow run carries a full `repository` object. We do not pass those
through. Three reasons:

1. **It is silently wrong history.** The embedded copy reflects the entity as of
   *fetch time*, not as of the event. An issue opened in 2021 carries the author's
   2026 avatar, bio and site-admin flag. A user of the raw table has no way to know.
2. **It is bulk.** The same user object is repeated on every row it touches.
3. **It breaks typing.** Nested objects and arrays-of-objects do not land cleanly in
   Parquet or Iceberg, which is the whole point of this connector.

What we keep instead is the **key needed to perform the join**, plus the small number
of identity attributes that are stable enough to be treated as part of the key:

| Referenced entity | Kept as |
| --- | --- |
| user | `user_id`, `user_login`, `user_type` |
| repository | `repository` (`owner/name`), `repository_id` |
| milestone | `milestone_id`, `milestone_number`, `milestone_title` |
| labels | `labels` (array of `{id, name, description}`) plus a `label_names` projection |
| assignees | `assignees` (array of `{id, login, type}`) plus an `assignee_logins` projection |

Handles and full names are mutable in theory and effectively stable in practice, so
carrying both an id and a human-readable name is a deliberate exception, not a
violation of the rule.

The canonical thing *not* to do: putting `stargazers_count` on every issue because
the API happened to include the repository object. That is a repository attribute
riding along on a child row.

## 3. Point-in-time facts are an exception, and are kept

A value that describes *the record itself* belongs on the record even if it is
sourced from another entity. The test is whether the value would be wrong if you
recomputed it later:

- `author_association` — the author's relationship to the repo **at the time** they
  commented. Recomputing it from a `users` table gives a different answer.
- `head_sha` / `base_sha` / `parent_shas` / `commit_sha` — immutable git identifiers.
- `user_type` — distinguishes bot activity from human activity, which is analytically
  load-bearing and unrecoverable without it.
- `commit_author_name` / `commit_author_email` — what git recorded, not what the
  GitHub account says today.

## 4. Types are chosen for Parquet and Iceberg, not for JSON

- Every schema sets `additionalProperties: false`, and every field the API returns is
  either declared or explicitly removed via `RemoveFields`. A field that is neither
  is a bug: the record would carry a column the destination was never told about.
- Every record selector sets `schema_normalization: Default`, so values are cast to
  the declared schema after transformations run. This is what makes `id` an `integer`
  rather than "whatever Jinja produced".
- Timestamps are `format: date-time` with `airbyte_type: timestamp_with_timezone`.
- Ids, counts, positions and line numbers are `integer`. Git SHAs and `node_id` are
  `string` despite the `_id` suffix.
- Every array declares an explicit `items` schema. An array of objects declares the
  object's `properties` and `additionalProperties: false` like any other schema, and
  every element is pruned to those properties with a wildcard `RemoveFields` pointer
  (`["labels", "*", "color"]`; dpath globs index into lists).
- **Never emit parallel arrays that a consumer has to re-zip by position.** An earlier
  revision shipped `label_ids` and `label_names` side by side and asked the reader to
  trust that index `i` lined up across both columns, through every hop of the pipeline.
  Both columns were typed, but recovering "which id goes with which name" depended on
  an unwritten convention, which is the failure mode the typing rules exist to prevent.

### Choosing the shape of a repeated field

Four cases, in the order the questions should be asked:

1. **The element has its own lifecycle or its own mutable state → separate stream.**
   `releases.assets` looks like a struct array but carries `download_count`, a counter
   that moves independently of the release. Inlining it recreates the as-of-fetch
   problem from rule 2 on a nested field.
2. **One scalar functionally determines the rest of the element → array of primitives.**
   `commits.parents` is a list of objects whose every field is a URL derived from
   `sha`, so `parent_shas` is lossless and a struct would be bulk.
3. **The element is a value with several independent attributes → array of structs, no
   projection.** `workflow_jobs.steps` has a name, a status, a conclusion and two
   timestamps; no single field summarizes it, so there is nothing honest to project.
4. **The element is a reference to an entity → array of structs plus one projection
   column.** `labels` and `assignees` are key tuples. The struct array keeps the
   association intact and the projection (`label_names`, `assignee_logins`) is the
   access path almost every query wants, typed as a plain `array<string>`.

A projection column is a convenience, never the only copy of a fact. If dropping the
struct array would lose information, the projection is not enough.

### What an array of structs lands as today

The Iceberg and S3 Data Lake destinations currently stringify object-valued columns
(`AirbyteTypeToIcebergSchema` is called with `stringifyObjects = true` for every column
except `_airbyte_meta`), so `labels` lands as `list<string>` where each element is one
self-contained JSON object. That is a destination policy, not a Parquet or Iceberg
limitation — `list<struct<id: long, name: string>>` is an ordinary Iceberg type.

This is why the shape is still correct to emit: each element carries its own id and
name, so nothing has to be re-zipped even in the degraded form, and when the
destination stops stringifying, the same column becomes a native struct list with no
change here and no rename. Consumers on the projection columns never notice.

Stringification is an interim compatibility behavior, not the target. Do not design a
field around it, and do not use it as a reason to flatten something that is genuinely
repeated and structured.

### A note on `value_type` in `AddFields`

Do not set `value_type` on an `AddFields` entry. Jinja already returns native
integers, booleans and `None`; declaring a `value_type` makes the CDK fall back to the
rendered string when the value does not match, which turns every null into the literal
string `"None"`. `schema_normalization` does the casting correctly and after the fact.

## 5. URL policy

URLs are grouped into three kinds, and only two survive:

1. **Self links — kept.** `api_url` (the record's own REST URL, GitHub calls it `url`)
   and `html_url`. These are facts about the row, and an agent or human landing on the
   row should be able to navigate to it.
2. **Content downloads — kept.** `diff_url`, `patch_url`, `tarball_url`, `zipball_url`.
   Derivable only if you know the exact URL algorithm, and directly useful.
3. **Referenced-collection links — dropped.** `comments_url`, `statuses_url`,
   `timeline_url`, `events_url`, `labels_url`, `commits_url`, `jobs_url`, and friends.
   These are derivable from keys we already carry and are pure bulk.

Naming: `api_url` and `html_url` for the record's own entity; `<entity>_api_url` /
`<entity>_html_url` for anything referenced. Never a bare `url`, and never GitHub's
convention where a plain `_url` suffix silently means "the API one".

Where a referenced URL is dropped but the join matters, the join key is derived
instead — `comments.issue_number` and `review_comments.pull_request_number` are parsed
out of the URLs that are then removed.

## 6. Stream conventions

- Every stream carries `repository` (`owner/name`) and, where the API provides it,
  `repository_id`. The repository is a `ListPartitionRouter` over the configured
  repositories.
- Substreams use `SubstreamPartitionRouter` with `extra_fields` to carry the parent's
  `repository` down. Do not synthesize composite parent keys — an earlier revision of
  this connector shipped a `_review_key` field of the form `owner/repo::123` as a real
  column, which is exactly the sort of artifact that should never reach a destination.
- `issues` includes pull requests, matching Gen-1 and the underlying API. `is_pull_request`
  and `pull_request_number` make it cheap to join or anti-join against `pull_requests`.
- Streams whose endpoint supports `since` use a server-side `DatetimeBasedCursor`.
  Streams whose endpoint does not (`releases`, `stargazers`, `workflows`,
  `workflow_runs`) use `is_client_side_incremental: true`, which still gives incremental
  output at the cost of a full scan.

## 7. Current exclusions

- **No `users` stream.** `user_id` + `user_login` identify a user well enough for now,
  and the right source of user detail is a future `participants`-style stream rather
  than a global user dump.
- **No GraphQL.** Every stream here is REST. Gen-1 uses GraphQL for reaction counts,
  PR stats and Projects V2; those streams are deferred rather than reimplemented.
- **PAT authentication only.** Multi-token round-robin needs a rotating authenticator
  that the declarative CDK does not have yet, and the long-term credential shape (an
  array of typed credential objects vs. per-type arrays) is unresolved — including
  whether the platform handles secrets nested inside objects inside arrays.

## 8. Deferred streams

Candidates for referential completeness, in rough priority order: `teams`,
`team_members`, `collaborators`, `deployments`, `commit_comments`, `issue_events`,
`issue_labels`, `issue_milestones`, `projects_v2`, and a participants-style user
stream. All are REST-capable except `projects_v2`.

`release_assets` belongs here too, and for the reason in case 1 above rather than for
coverage: an asset's `download_count` is a moving counter that has no business being
inlined into a release row.
