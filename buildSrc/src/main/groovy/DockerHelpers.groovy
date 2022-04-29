import java.nio.file.Paths

class DockerHelpers {
    static String extractLabelValue(String dockerFile, String labelName) {
        def file = dockerFile instanceof File ? dockerFile : new File(dockerFile)
        return file.readLines()
                .grep({ it.startsWith('LABEL') && it.contains(labelName) })
                .get(0)
                .split('=')[1]
    }

    static String extractImageName(String dockerFile) {
        return extractLabelValue(dockerFile, "io.airbyte.name")
    }

    static String extractImageVersion(String dockerFile) {
        return extractLabelValue(dockerFile, "io.airbyte.version")
    }

    static String getDevTaggedImage(projectDir, dockerfileName) {
        def imageName = extractImageName(Paths.get(projectDir.absolutePath, dockerfileName).toString())
        def imageVersion = extractImageVersion(Paths.get(projectDir.absolutePath, dockerfileName).toString())

        if (System.getenv("BUILD_CANDIDATE_IMAGE") == "true" && System.getenv("PR_NUMBER") != null) {
            return "${imageName}:${imageVersion}-candidate-${System.getenv("PR_NUMBER")}"
        } else {
            return "${imageName}:dev"
        }
    }
}
