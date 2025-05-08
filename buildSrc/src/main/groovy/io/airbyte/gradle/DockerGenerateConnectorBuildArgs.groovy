package io.airbyte.gradle

import org.gradle.api.DefaultTask
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.provider.Property
import org.gradle.api.tasks.*
import org.yaml.snakeyaml.Yaml

/**
 * Reads `metadata.yaml` (if present) and emits
 * `${buildDir}/docker/buildArgs.properties`
 * so docker build tasks can consume per‑module arguments.
 */
class DockerGenerateConnectorBuildArgs extends DefaultTask {

    @InputFile
    final RegularFileProperty metadata = project.objects.fileProperty()

    @OutputFile
    final RegularFileProperty output = project.objects.fileProperty()

    @Internal
    final Property<Yaml> yaml = project.objects.property(Yaml).convention(new Yaml())

    @TaskAction
    void run() {
        def metaFile = metadata.get().asFile
        def outFile = output.get().asFile

        if (!metaFile.exists()) {
            outFile.text = ''          // keep Gradle’s cache happy
            return
        }

        Map root = yaml.get().load(metaFile.text) ?: [:]
        Map<String, ?> opts = ((root['data'] ?: [:])['connectorBuildOptions'] ?: [:]) as Map<String, ?>
        outFile.withPrintWriter { pw ->
            opts.each { k, v ->
                if (v != null) {
                    def key = k
                            .replaceAll(/([a-z0-9])([A-Z])/, '$1_$2') // camelCase → snake_case
                            .replace('-', '_')                        // dash → underscore
                            .toUpperCase(Locale.ROOT)
                    pw.println("${key}=$v")
                }
            }
            /* Always add CONNECTOR_NAME=<module‑directory>. This is used to defined the image's name. */
            pw.println("CONNECTOR_NAME=${project.projectDir.name}")
        }
    }
}
