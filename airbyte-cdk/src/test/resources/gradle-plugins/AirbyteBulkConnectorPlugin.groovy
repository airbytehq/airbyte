import org.gradle.api.Plugin
import org.gradle.api.Project

class AirbyteBulkConnectorPlugin implements Plugin<Project> {
    void apply(Project project) {
        project.extensions.create('airbyteBulkConnector', AirbyteBulkConnectorExtension)
    }
}

class AirbyteBulkConnectorExtension {
    String cdk = 'published'
}