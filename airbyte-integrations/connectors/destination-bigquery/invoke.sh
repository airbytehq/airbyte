/airbyte/base.sh $@

if test $1 = 'write' # && test $AIRBYTE_MATERIALIZATION_MODE = 'LEGACY_NORMALIZATION'
then
  # TODO parse args maybe? entrypoint.sh will reject unrecognized args... but `write` currently only accepts config and catalog anyway
  /airbyte/entrypoint.sh run ${@:2} --integration-type bigquery
fi
