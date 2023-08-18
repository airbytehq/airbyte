# Python Source CSV Export

This collection of tools is used to run the source and capture it's AirbyteMessages and convert them into CSV files. This is useful if you want to manually inspect this data or load it into a database manually.

To be fast, we make use of parallel processing per-stream and only using command-line tools. This works by the main file (`main.sh`) running the source via python and tee-ing the output of RECORDS to sub-scripts which use `jq` to convert the records into CSV-delimited output, which we finally write to disk.

As we read the connector config files, e.g. `--config secrets/config.json --state secrets/state.json --catalog integration_tests/configured_catalog.json`, you can manually step forward your sync if you need to read and store the input in chunks.

## The road to 1TB of faker data

There's commentary on this at https://github.com/airbytehq/airbyte/pull/20558, along with some cool SQL tricks.

- 2 Billion faker users for 1TB: `10,000,000*(1024/5.02) = 2,039,840,637`
- 200 Million faker users for 100GB: `10,000,000*(100/5.02) = 199,203,187`
- 20 Million faker users for 10GB: `10,000,000*(10/5.02) = 19,920,318`

But let's assume we don't have 1TB of local hard disk. So, we want to make 10 chunks of data, each around 100GB in size.

**`config.json`**

```json
{
  "count": 2039840637,
  "seed": 0
}
```

**`state.json`**

At the end of every sync, increment the `id` in the users stream and the `user_id` in the purchases stream by `203984064`

```json
[
  {
    "type": "STREAM",
    "stream": {
      "stream_state": {
        "id": 0
      },
      "stream_descriptor": {
        "name": "users"
      }
    }
  },
  {
    "type": "STREAM",
    "stream": {
      "stream_state": {
        "id": 0,
        "user_id": 0
      },
      "stream_descriptor": {
        "name": "purchases"
      }
    }
  },
  {
    "type": "STREAM",
    "stream": {
      "stream_state": {
        "id": 0
      },
      "stream_descriptor": {
        "name": "products"
      }
    }
  }
]
```

Finally, ensure that you've opted-into all the streams in `integration_tests/configured_catalog.json`

## TODO

- This is currently set up very manually, in that we build bash scripts for each stream and manually populate the header information. This information all already lives in the connector's catalog. We probably could build these bash files on-demand with a python script...
