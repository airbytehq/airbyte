FROM temporalio/auto-setup:1.13.0

ENV TEMPORAL_HOME /etc/temporal

ENTRYPOINT ["/etc/temporal/entrypoint.sh", "bash"]

COPY bin/scripts/wait-for-db-upgrade.sh /etc/temporal/wait-for-db-upgrade.sh
