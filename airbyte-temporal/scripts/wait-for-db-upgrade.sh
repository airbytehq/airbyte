#!/usr/bin/env bash

startTemporal() {
  SERVICES="${SERVICES:-}"
  SERVICE_FLAGS="${SERVICE_FLAGS:-}"

  if [ -z "${SERVICE_FLAGS}" ] && [ -n "${SERVICES}" ]; then
      # Convert semicolon (or comma, for backward compatibility) separated string (i.e. "history:matching")
      # to valid flag list (i.e. "--service=history --service=matching").
      IFS=':,' read -ra SERVICE_FLAGS <<< "${SERVICES}"
      for i in "${!SERVICE_FLAGS[@]}"; do SERVICE_FLAGS[$i]="--service=${SERVICE_FLAGS[$i]}"; done
  fi

  exec temporal-server --env docker start "${SERVICE_FLAGS[@]}"
}

dockerize -template ./config/config_template.yaml:./config/docker.yaml

until startTemporal 2> /dev/null
do
    echo "Waiting for db migration"
    sleep 2
    # sh ./start-temporal.sh
done

echo "Temporal is started"
