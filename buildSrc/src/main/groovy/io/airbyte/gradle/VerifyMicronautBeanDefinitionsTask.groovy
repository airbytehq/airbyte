package io.airbyte.gradle

import org.gradle.api.DefaultTask
import org.gradle.api.GradleException
import org.gradle.api.file.ConfigurableFileCollection
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.provider.Property
import org.gradle.api.tasks.*

/**
 * Loads every Micronaut bean definition that KSP generated for one source set and fails the build
 * if any of them does not link.
 *
 * Micronaut discovers bean definitions through a service loader that silently drops any
 * `$Definition` class which fails to load (VerifyError, NoClassDefFoundError, ...). The bean then
 * just vanishes from the context and the failure only surfaces later, as a NoSuchBeanException at
 * an unrelated injection point, or not at all when the bean is optional. inject-kotlin 4.8.0-4.10.x
 * is known to emit unverifiable bytecode for Kotlin constructors that combine a default value with
 * a primitive parameter (micronaut-core #11407/#11502, fixed in 5.2.15 by #13041), so this task
 * runs after compilation and before any test task.
 *
 * Verification happens in-process: the JVM verifies a class when it links it, and
 * `Class.forName(name, true, loader)` links and initializes it. The loader is a throwaway
 * URLClassLoader over the source set's runtime classpath whose parent is the platform class
 * loader, so nothing from Gradle's own classpath leaks in.
 */
abstract class VerifyMicronautBeanDefinitionsTask extends DefaultTask {

    /** `build/generated/ksp/<sourceSet>/resources/META-INF/micronaut/io.micronaut.inject.BeanDefinitionReference`. */
    @InputDirectory
    @PathSensitive(PathSensitivity.RELATIVE)
    @SkipWhenEmpty
    @IgnoreEmptyDirectories
    abstract DirectoryProperty getReferenceDirectory()

    /** The source set's runtime classpath, including its own classes and resources directories. */
    @Classpath
    abstract ConfigurableFileCollection getClasspath()

    @Input
    abstract Property<String> getSourceSetName()

    @OutputFile
    abstract RegularFileProperty getReport()

    @TaskAction
    void verify() {
        File referenceDir = referenceDirectory.get().asFile
        List<String> classNames = referenceDir.listFiles()
                .findAll { it.isFile() }
                .collect { it.name }
                .sort()
        List<URL> urls = classpath.files.collect { it.toURI().toURL() }
        Map<String, String> failures = new TreeMap<>()
        URLClassLoader loader = new URLClassLoader(urls as URL[], ClassLoader.platformClassLoader)
        try {
            for (String className : classNames) {
                try {
                    Class.forName(className, true, loader)
                } catch (Throwable t) {
                    failures[className] = describe(t)
                }
            }
        } finally {
            loader.close()
        }

        File reportFile = report.get().asFile
        reportFile.parentFile.mkdirs()
        reportFile.withPrintWriter { pw ->
            pw.println("source set: ${sourceSetName.get()}")
            pw.println("bean definitions checked: ${classNames.size()}")
            pw.println("failures: ${failures.size()}")
            failures.each { name, message -> pw.println("${name}\n    ${message}") }
        }

        if (!failures.isEmpty()) {
            String details = failures.collect { name, message -> "  - ${name}\n      ${message}" }.join('\n')
            throw new GradleException(
                    "${failures.size()} of ${classNames.size()} Micronaut bean definitions in ${project.path} " +
                    "(source set '${sourceSetName.get()}') fail to load; Micronaut would silently drop these beans.\n" +
                    details +
                    "\nKotlin constructors with a default value and a primitive (Int/Long/Boolean/...) parameter " +
                    "are known to trigger this on inject-kotlin 4.8.0-4.10.x: remove the default or add an " +
                    "@Inject secondary constructor without defaults.")
        }
        logger.lifecycle("Verified ${classNames.size()} Micronaut bean definitions in ${project.path} (source set '${sourceSetName.get()}')")
    }

    private static String describe(Throwable t) {
        String message = "${t.class.name}: ${t.message}"
        Throwable cause = t.cause
        int depth = 0
        while (cause != null && depth < 5) {
            message += " <- ${cause.class.name}: ${cause.message}"
            cause = cause.cause
            depth++
        }
        return message
    }
}
