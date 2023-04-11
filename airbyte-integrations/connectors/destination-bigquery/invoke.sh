echo $@

/airbyte/base.sh $@

# if test $AIRBYTE_MATERIALIZATION_MODE = 'LEGACY_NORMALIZATION'
# then
#   # TODO parse args. or maybe just be ok with hardcoding these filenames?
  /airbyte/entrypoint.sh run --config destination_config.json --catalog destination_catalog.json --integration-type bigquery
# fi
