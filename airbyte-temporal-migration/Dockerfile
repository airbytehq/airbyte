FROM temporalio/admin-tools:1.13.0

ENV TEMPORAL_HOME /etc/temporal

COPY bin/scripts/upgrade-db-version.sh upgrade-db-version.sh

ENTRYPOINT ["./upgrade-db-version.sh"]
