FROM amazoncorretto:19

ARG DOCKER_BUILD_ARCH=amd64

WORKDIR /app

RUN yum install -y tar

# Add the Datadog Java APM agent
ADD https://dtdg.co/latest-java-tracer dd-java-agent.jar

# Add the OpenTelemetry Java APM agent
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar opentelemetry-javaagent.jar
