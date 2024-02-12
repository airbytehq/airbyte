package io.airbyte.cdk.integrations.base.context;

import io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource;
import io.micronaut.configuration.picocli.MicronautFactory;
import io.micronaut.context.ApplicationContext;
import io.micronaut.context.ApplicationContextBuilder;
import io.micronaut.context.env.CommandLinePropertySource;
import io.micronaut.context.env.Environment;
import picocli.CommandLine;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.ARGS_CATALOG_KEY;

public class AirbyteConnectorRunner {

    public static <R extends Runnable> void run(final Class<R> cls, final String... args) {
        ApplicationContextBuilder builder = buildApplicationContext(cls, args);
        try (ApplicationContext ctx = builder.start()) {
            run(cls, ctx, args);
        }
    }

    public static <R extends Runnable> void run(final Class<R> cls, final ApplicationContext ctx, final String... args) {
        final CommandLine commandLine = new CommandLine(cls, new MicronautFactory(ctx));
        commandLine.execute(args);
    }

    private static ApplicationContextBuilder buildApplicationContext(final Class<?> cls, final String[] args) {
        io.micronaut.core.cli.CommandLine commandLine = io.micronaut.core.cli.CommandLine.parse(args);
        ConnectorConfigurationPropertySource connectorConfigurationPropertySource = new ConnectorConfigurationPropertySource(commandLine);
        CommandLinePropertySource commandLinePropertySource = new CommandLinePropertySource(commandLine);
        return ApplicationContext
                .builder(cls, Environment.CLI)
                .propertySources(connectorConfigurationPropertySource, commandLinePropertySource);
    }
}
