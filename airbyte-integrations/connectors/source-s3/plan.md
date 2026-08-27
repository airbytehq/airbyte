# Implementation Plan: Password-Protected ZIP Support in `source-s3`

> **Status:** Phase 1 (ZipCrypto) and Phase 2 (AES-256 / WinZip AES) are both implemented in `source_s3/v4/config.py`, `zip_reader.py`, and `stream_reader.py`, with unit tests in `unit_tests/v4/test_zip_reader.py` and `test_stream_reader.py`. Phase 2 ended up using the `cryptography` package (already an existing transitive dependency) rather than `pyzipper` as originally sketched below — see the "Phase 2" section for why, and for the one shipped scope reduction (HMAC authentication is not verified).

## Background

`source-s3` (`airbyte-integrations/connectors/source-s3`) already supports reading files packaged inside plain (unencrypted) `.zip` archives, but the implementation is entirely bespoke to this connector — it is not part of the shared Airbyte file-based CDK (`airbyte_cdk.sources.file_based`). ZIP is not a selectable "format" in the config spec; it is auto-detected purely by the `.zip` filename suffix.

Key files:

- `source_s3/v4/zip_reader.py` — `ZipFileHandler` (lists archive contents by fetching only the ZIP central directory via S3 HTTP range requests, avoiding a full download just to enumerate entries), `RemoteFileInsideArchive` (a `RemoteFile` subclass carrying `start_offset`/`compressed_size`/`uncompressed_size`/`compression_method`), `DecompressedStream` (an `io.IOBase` that streams and decompresses a single archive entry on demand using stdlib `zipfile` internals), `ZipContentReader` (line-buffered text wrapper handed to the inner CSV/JSONL/Avro/Parquet parser).
- `source_s3/v4/stream_reader.py` — `SourceS3StreamReader._handle_zip_file()` builds one `RemoteFileInsideArchive` per entry during listing; `open_file()` wires up `DecompressedStream` + `ZipContentReader` when a file turns out to be `RemoteFileInsideArchive`.
- `source_s3/v4/config.py` — `Config(AbstractFileBasedSpec)` and `S3FileBasedStreamConfig(FileBasedStreamConfig)`. No zip-specific config exists today.

There is currently no password/encryption handling anywhere in the connector: no `pyzipper` dependency, no AES support, no `password` field. Encrypted entries would currently fail with an opaque error deep in decompression (or silently produce garbage).

Two decisions were made up front to scope this work:

1. **Encryption schemes: phased.** Ship legacy **ZipCrypto** support first (no new dependency, lower risk, reuses a pattern the codebase already relies on — private stdlib APIs). Follow up with **AES-256** (WinZip AES) support, which is what most security/compliance-conscious data partners actually use in practice.
2. **Password scope: connector-wide.** The password is configured once globally on `Config`, applying to every zip the connector touches in a sync. Simpler than a per-stream field — no need to resolve which stream a given listing call belongs to — at the cost of not supporting different passwords for different streams/partners within one source.

A useful architectural fact discovered during investigation: the central directory metadata Airbyte already fetches during listing (`zipfile.ZipInfo`) contains `flag_bits` (bit 0 = entry is encrypted) and `compress_type` (`99` = WinZip AES marker, with the real compression method + key size stored in the `0x9901` extra-field record). So detecting encryption, and which scheme, is free at listing time — no extra S3 calls needed.

---

## 1. Config schema changes

Add a new field directly to `Config` (not `S3FileBasedStreamConfig`) in `source_s3/v4/config.py`:

```python
password: Optional[str] = Field(
    title="Zip Password",
    description="Password to decrypt password-protected ZIP archives encountered during the sync.",
    airbyte_secret=True,
    default=None,
    order=7,
)
```

This sits alongside the other connector-level fields (`bucket`, `aws_access_key_id`, etc.) rather than nested under `streams`, so it needs no special handling in `Config.schema()` — it's a plain top-level field like any other, unlike the per-stream `skip_full_check_for_parquet` flag which requires hand-copying schema between `S3FileBasedStreamConfig` and the parent spec.

No changes are needed to `S3FileBasedStreamConfig` at all. Existing configs need no migration — the field defaults to `None`, so unencrypted zips are entirely unaffected. Double-check `legacy_config_transformer.py` (referenced in `config.py`'s docstring warning) in case the v3→v4 config migration path needs to carry a password through as well.

---

## 2. Threading the password from config → reader

Because the password is connector-wide, this step is trivial: `SourceS3StreamReader` already holds the entire `Config` object on `self.config` from the moment the source sets it (see the `config` setter in `stream_reader.py`), and `self.config` is accessible from every method on the reader instance — no new parameters need to be threaded through `get_matching_files` → `_page` → `_handle_file` → `_handle_zip_file`.

`_handle_zip_file` reads `self.config.password` directly when constructing each `RemoteFileInsideArchive`. Three more fields are stamped onto that object, sourced from the `ZipInfo` at the same point, since these are per-entry facts rather than connector-wide ones: `flag_bits: int` (exposed via an `is_encrypted` property, bit 0), `crc: int` (used to validate a ZipCrypto password), and `extra: bytes` (the raw central-directory extra field, parsed on demand to pull out the WinZip AES strength/real-compression-method when `compression_method == 99`). Storing the raw `extra` bytes rather than a pre-parsed `aes_strength` field (as originally sketched here) turned out simpler: one generic field instead of a second one-off attribute, parsed lazily only when actually needed.

`open_file()` also already has `self.config` in scope, so `DecompressedStream` construction can pull the password straight from `self.config.password` rather than needing it stashed on the file object first — one less thing carried on `RemoteFileInsideArchive`. `open_file()`'s signature doesn't change.

**Known limitation to document:** one password applies to every zip the connector touches in a given sync. If a source needs to pull zips from multiple partners using different passwords, this design doesn't support that (a future per-stream field remains a viable follow-up if that need arises, at the cost of the glob-matching plumbing discussed and rejected here as unnecessary complexity for the common case).

---

## 3. Decryption architecture — Phase 1: ZipCrypto

New small module, e.g. `source_s3/v4/zip_decrypter.py`, wrapping stdlib's private `zipfile._ZipDecrypter(password)` class — consistent with the existing code's precedent of relying on private stdlib internals (`zipfile._get_decompressor` is already used in `DecompressedStream`). No new dependency required.

`DecompressedStream` gains a `_reset_decryptor()` alongside its existing `_reset_decompressor()`, and `_decompress_chunk` becomes decrypt-then-decompress for encrypted entries. The 12-byte ZipCrypto encryption header sits immediately at `file_start`, so `_calculate_actual_start`'s math shifts by 12 bytes for encrypted entries; everything else (buffering, `read()`, byte-range math against S3) is unchanged.

Convenient architectural fact that de-risks this: `DecompressedStream.seek()` only has two anchor points in `offset_map` (`0` and `uncompressed_size`), so any seek other than to the exact end already restarts decompression from byte 0 and reads forward sequentially. That is exactly what a stream cipher needs — ZipCrypto's keystream evolves per byte from the start of the entry — so no rearchitecture of seeking is required; decryptor state simply resets in lockstep with the decompressor via the existing reset hook.

---

## 4. Decryption architecture — Phase 2: AES-256 (WinZip AES) — as shipped

The original idea below was to depend on `pyzipper` and reuse its internal decrypter class. That changed during implementation: `pyzipper`'s whole raison d'être is its high-level `ZipFile`/`AESZipFile` API, which — like stdlib `zipfile` in Phase 1 — assumes it owns the whole local file. Our architecture never uses that API (it never has; Phase 1 doesn't either), so depending on `pyzipper` would mean taking on an entire library just to reach into one internal, undocumented class. Instead, `zip_reader.py` depends directly on `cryptography` (`Cipher`/`algorithms.AES`/`modes.ECB`), which turned out to already be a resolved transitive dependency (via `google-auth`) — so this added *zero* new third-party footprint, better than the original plan.

The WinZip AES-2 format, confirmed against the public specification: a 0x9901 extra-field record (parsed from the central directory's `extra` bytes, always present regardless of the range-read/central-directory-only listing approach) gives the AES strength (1/2/3 → 128/192/256-bit) and the *real* compression method (the central directory's own `compress_type` is overwritten with the sentinel value `99`). The entry's data is `salt (8/12/16 bytes) + password-verification (2 bytes) + ciphertext + HMAC-SHA1-80 (10 bytes)`. The encryption key and the 2-byte password-verification value are both derived via `hashlib.pbkdf2_hmac("sha1", password, salt, 1000, dklen=...)` — stdlib has this built in, no library needed.

The one genuine wrinkle: WinZip's AES-CTR uses a **little-endian** 16-byte counter starting at 1, incremented per 16-byte block — `cryptography`'s own high-level CTR mode increments its counter as a **big-endian** integer, so it can't be used directly (this mismatch is exactly why `pyzipper` has to work around the same library internally). The fix: drive the raw AES-ECB block primitive by hand (`_AesCtrCipher` in `zip_reader.py`), computing each block's little-endian counter value ourselves and XOR-ing against the ciphertext — a well-documented, standard CTR construction, just not the one the library automates for us.

Structurally, this reuses the exact same shape as Phase 1: shift `file_start` past the salt+password-verification bytes, shrink `compressed_size` by that same overhead plus the trailing 10-byte HMAC, and the existing `read()`/`seek()` machinery needs no changes. `DecompressedStream` now has a single `_make_decrypter` factory (a zero-arg callable producing a fresh, primed decrypter) set by whichever of `_init_zip_crypto_decryption`/`_init_aes_decryption` applies; `_reset_decompressor()` (called on every `seek()`) just calls it again. Both a ZipCrypto closure and an `_AesCtrCipher` instance satisfy the same "stateful, sequential, bytes→bytes callable" contract, so `_decompress_chunk` doesn't need to know which scheme it's dealing with.

**Known, intentional scope reduction:** the trailing 10-byte HMAC-SHA1-80 authentication code is not verified. It's a tamper/corruption check, not something decryption correctness depends on — verifying it would mean reading past the "compressed_size" the rest of the class already relies on and tracking a running HMAC across arbitrary `read()`/`seek()` calls, for a benefit (detecting deliberate tampering or S3-level corruption) this connector's threat model doesn't especially need. The cheap 2-byte password-verification check (done upfront, like ZipCrypto's 12-byte header check) already gives a fast, clear "wrong password" error; a corrupted-but-correctly-passworded file would surface as a decompression error instead of an integrity-check error.

---

## 5. Error handling

Three distinct, actionable errors instead of one confusing failure deep in the pipeline:

- Encrypted entry with no password configured on `Config` → config error raised at discovery/listing time (we already know both facts then), not a mid-sync failure.
- Wrong password → ZipCrypto's 12-byte header check (CRC-derived) or AES's 2-byte password-verification value catches this immediately for either scheme; surfaced as a clear "incorrect zip password" error rather than a garbled decompression failure downstream.
- Unrecognized/unparseable AES extra field (an AES strength byte we don't recognize, or a missing 0x9901 record) → explicit, specific error, never a silent pass-through that emits corrupt records.

---

## 6. Dependencies

- Phase 1 (ZipCrypto): none — stdlib only.
- Phase 2 (AES-256): `cryptography` (added explicitly to `pyproject.toml`), already resolved transitively via `google-auth` — no new third-party footprint.

---

## 7. Testing

**Unit tests** (`unit_tests/v4/test_zip_reader.py`): both stdlib `zipfile` and `pyzipper` turned out unusable for building password-protected test fixtures — stdlib can *read* ZipCrypto but never learned to *write* it, and pulling in `pyzipper` just to author fixtures would defeat the point of not depending on it. Instead, both schemes have small, from-scratch, independent reference implementations in the test file (`_zip_crypto_encrypt`, `_aes_ctr_transform` + PBKDF2/HMAC via stdlib) used only to build genuine encrypted zip byte fixtures — deliberately kept separate from the production `_AesCtrCipher`/`zipfile._ZipDecrypter` code paths so a bug can't "cancel itself out" by being used symmetrically on both sides of a round-trip test. Covers, for both schemes: correct password round trip, seek-then-read correctness, wrong password, missing password, and (AES-specific) all three key strengths, an unparseable extra field, and an unrecognized strength byte.

**Integration tests**: add a real encrypted fixture zip under `integration_tests/` (following the existing `minio_data.zip` pattern), a `password` secret, and expected-records fixtures, mirroring the existing `zip_{csv,jsonl,avro,parquet}` test scenarios. Extend `acceptance-test-config.yml` accordingly.

**Config tests**: update the existing config/schema tests to assert the new top-level `password` field appears correctly in `Config.schema()`'s `properties`.

---

## 8. Docs & rollout

- Changelog entry in `docs/integrations/sources/s3.md`.
- Version bump in `pyproject.toml` / `metadata.yaml` — minor version, since this is an additive, backward-compatible field.
- Phase 1 shipped first (v4.16.0) to validate the plumbing with zero new dependencies; Phase 2 (AES-256, v4.17.0) followed once a real customer file surfaced the AES limitation directly, confirming AES-256 is in fact the scheme in active use, not just a theoretical "most partners use this" concern.
