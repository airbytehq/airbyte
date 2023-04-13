set -e

/airbyte/base.sh $@

if test $1 = 'write' # && test $NORMALIZATION_TECHNIQUE = 'LEGACY'
then
  # TODO parse args maybe? entrypoint.sh will reject unrecognized args... but `write` currently only accepts config and catalog anyway
  /airbyte/entrypoint.sh run ${@:2} --integration-type bigquery | java -cp "/airbyte/lib/*" io.airbyte.integrations.destination.bigquery.NormalizationLogParser
fi
