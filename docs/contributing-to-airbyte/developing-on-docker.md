# Developing on docker

## Incrementality 

The docker build is fully incremental for the platform build, which means that it will only build an image if it is needed. We need to keep it that 
way.
The top level `build.gradle` file defines several convenient tasks for building a docker image.
1) The `copyGeneratedTar` task copies a generated TAR file from a default location into the default location used by the [docker plugin](https://github.com/bmuschko/gradle-docker-plugin).
2) The `buildDockerImage` task is a convenience class for configuring the above linked docker plugin that centralizes configuration logic commonly found in our dockerfiles.
3) Makes the `buildDockerImage` task depend on the Gradle `assemble` task.

These tasks are added to a subproject if the subproject has a `gradle.properties` file with the `dockerImageName` property.

This property is sets the build docker image's name.

## Adding a new docker build

Once you have a `Dockerfile`, generating the docker image is done in the following way:
- specify the artifact name, the project directory, the version, and the tag.
- make sure that the Dockerfile is properly copied to the docker context dir before building the image
- make the build docker task to depend on the `assemble` task.

For example:
```groovy
Task dockerBuildTask = getDockerBuildTask("cli", project.projectDir, rootProject.ext.version, rootProject.ext.image_tag)
dockerBuildTask.dependsOn(copyDocker)
assemble.dependsOn(dockerBuildTask)
```

If you need to add files in your image you need to copy them in `build/docker/bin` first. The need to happen after the `copyDocker` task.
The `copyDocker` task clean up the `build/docker` folder as a first step.

For example:
```groovy
task copyScripts(type: Copy) {
    dependsOn copyDocker

    from('scripts')
    into 'build/docker/bin/scripts'
}

Task dockerBuildTask = getDockerBuildTask("init", project.projectDir, rootProject.ext.version, rootProject.ext.image_tag)
dockerBuildTask.dependsOn(copyScripts)
assemble.dependsOn(dockerBuildTask)
```

## Building the docker images

The gradle task `generate-docker` allows to build all the docker images.

## Handling the OSS version

The docker images that are running using a jar need to the latest published OSS version on master. Here is how it is handle:

### Existing modules

The version should already be present. If a new version is published while a PR is open, it should generate a conflict, that will prevent you from 
merging the review. There are scenarios where it is going to generate and error (The Dockerfile is moved for example), the way to avoid any issue 
is to:
- Check the `.env` file to make sure that the latest version align with the version in the PR
- Merge the `master` branch in the PR and make sure that the build is working right before merging.

If the version don't align, it will break the remote `master` build.

The version will be automatically replace with new version when releasing the OSS version using the `.bumpversion.cfg`.

### New module

This is trickier than handling the version of an exiting module.
First your docker file generating an image need to be added to the `.bumpversion.cfg`. For each and every version you want to build with, the 
docker image will need to be manually tag and push until the PR is merge. The reason is that the build has a check to know if all the potential 
docker images are present in the docker repository. It is done the following way:
```shell
docker tag 7d94ea2ad657 airbyte/temporal:0.30.35-alpha
docker push airbyte/temporal:0.30.35-alpha
```
The image ID can be retrieved using `docker images` or the docker desktop UI.
