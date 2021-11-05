# Developing on docker

## Incrementality 

The docker build is fully incremental for the platform build, which means that it will only build an image if it is needed. We need to keep it that 
way.
A task generator, `getDockerBuildTask`, is available for building a docker image for any given module. Behind the scene, it will generate a 
task which will run the build of a docker image in a specific folder. The goal is to make sure that we have an isolated 
context which helps with incrementality. All files that need to be present in the docker image will need to be copy into this folder. The generate 
method takes 2 arguments:
- The image name, for example if `foo` is given as an image name, the image `airbyte/foo` will be created
- The project directory folder. It is needed because the `getDockerBuildTask` is declared in the rootProject

## Adding a new docker build

Once you have a `Dockerfile`, generating the docker image is done in the following way:
- specify the artifact name and the project directory,
- make sure that the Dockerfile is properly copied to the docker context dir before building the image
- make the build docker task to depend on the `assemble` task.

For example:
```groovy
Task dockerBuildTask = getDockerBuildTask("cli", project.projectDir)
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

Task dockerBuildTask = getDockerBuildTask("init", project.projectDir)
dockerBuildTask.dependsOn(copyScripts)
assemble.dependsOn(dockerBuildTask)
```
