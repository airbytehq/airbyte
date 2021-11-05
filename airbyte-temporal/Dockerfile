FROM temporalio/auto-setup:1.13.0

ENV TEMPORAL_HOME /etc/temporal

COPY bin/scripts/update-and-start-temporal.sh update-and-start-temporal.sh

ENTRYPOINT ["/bin/bash"]
