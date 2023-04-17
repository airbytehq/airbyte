set -e
set -o pipefail

/airbyte/base.sh $@

if test $1 = 'write' && test $NORMALIZATION_TECHNIQUE = 'LEGACY'
then
  echo '{"type": "LOG","log":{"level":"INFO","message":"Starting in-connector normalization"}}'
  # the args in a write command are `write --catalog foo.json --config bar.json`
  # so if we remove the `write`, we can just pass the rest directly into normalization
  /airbyte/entrypoint.sh run ${@:2} --integration-type bigquery | java -cp "/airbyte/lib/*" io.airbyte.integrations.destination.normalization.NormalizationLogParser
  echo '{"type": "LOG","log":{"level":"INFO","message":"Completed in-connector normalization"}}'
fi
