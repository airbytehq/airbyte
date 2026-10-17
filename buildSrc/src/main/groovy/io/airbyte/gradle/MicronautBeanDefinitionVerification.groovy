package io.airbyte.gradle

import org.gradle.api.Project
import org.gradle.api.Task
import org.gradle.api.tasks.SourceSet
import org.gradle.api.tasks.TaskProvider
import org.gradle.api.tasks.testing.Test

/**
 * Registers one {@link VerifyMicronautBeanDefinitionsTask} per source set (named
 * `verifyMicronautBeanDefinitions<SourceSet>`, skipped when the source set has no KSP output),
 * an aggregate `verifyMicronautBeanDefinitions` task, and wires them so that `check` and every
 * {@link Test} task fail on a broken bean definition before running a single test.
 */
class MicronautBeanDefinitionVerification {

    static final String AGGREGATE_TASK_NAME = 'verifyMicronautBeanDefinitions'

    static void configure(Project project) {
        if (project.tasks.names.contains(AGGREGATE_TASK_NAME)) {
            return
        }
        TaskProvider<Task> aggregate = project.tasks.register(AGGREGATE_TASK_NAME) {
            group = 'verification'
            description = 'Loads every KSP-generated Micronaut bean definition and fails on classes the JVM rejects.'
        }

        project.sourceSets.all { SourceSet sourceSet ->
            String taskName = AGGREGATE_TASK_NAME + sourceSet.name.capitalize()
            TaskProvider<VerifyMicronautBeanDefinitionsTask> verifyTask =
                    project.tasks.register(taskName, VerifyMicronautBeanDefinitionsTask) {
                        group = 'verification'
                        description = "Loads the Micronaut bean definitions generated for the '${sourceSet.name}' source set."
                        sourceSetName.set(sourceSet.name)
                        referenceDirectory.set(project.layout.buildDirectory.dir(
                                "generated/ksp/${sourceSet.name}/resources/META-INF/micronaut/io.micronaut.inject.BeanDefinitionReference"))
                        classpath.from(sourceSet.output, sourceSet.runtimeClasspath)
                        report.set(project.layout.buildDirectory.file("reports/micronaut-bean-definitions/${sourceSet.name}.txt"))
                        dependsOn(sourceSet.classesTaskName)
                    }
            aggregate.configure { dependsOn(verifyTask) }
        }

        project.tasks.named('check').configure { dependsOn(aggregate) }

        project.tasks.withType(Test).configureEach { Test testTask ->
            if (testTask.name == 'test') {
                // The unit test classpath only sees main, test and testFixtures.
                testTask.dependsOn(project.tasks.matching {
                    it.name ==~ /verifyMicronautBeanDefinitions(Main|Test|TestFixtures)/
                })
            } else {
                // integrationTest* tasks see every source set.
                testTask.dependsOn(aggregate)
            }
        }
    }
}
