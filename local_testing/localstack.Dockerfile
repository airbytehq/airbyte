FROM localstack/localstack:4.12.0
COPY --chown=localstack ./setup_localstack.sh /etc/localstack/init/ready.d/init-aws.sh
RUN chmod u+x /etc/localstack/init/ready.d/init-aws.sh
