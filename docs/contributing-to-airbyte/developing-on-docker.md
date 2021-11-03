# Developing on docker

## Version

This doc is relevant starting from the version 0.30.26-alpha. Prior to that, it was another design.

## Incrementality 

The docker build is fully incremental, which means that it will only build an image if it is needed. We need to keep it that way.
A task, `buildDockerImage`, is available for building a docker image for any given module. Behind the scene, it will create a dedicated folder in 
the `build` folder of a module and copy the `Dockerfile` in it. The goal is to make sure that we have an isolated context which helps with 
incrementality. All files that need to be present in the docker image will need to be copy into this folder.

## Adding a new docker build

Once you have a `Dockerfile`, generating the docker image is done in the following way:
- specify the artifact name,
- make the build docker task to depend on the `assemble` task.

For example:
```groovy
project.properties.put("artifactName" , "cli")
assemble.dependsOn(buildDockerImage)
```

If you need to add files in your image you need to copy them in `build/docker/bin` first. The need to happen after the `copyDocker` task.
The `copyDocker` task clean up the `build/docker` folder.

For example:
```groovy
task copyGeneratedTar(type: Copy) {
    dependsOn copyDocker
    dependsOn distTar

    from('build/distributions') {
        include 'airbyte-workers-*.tar'
    }
    into 'build/docker/bin'
}

project.properties.put("artifactName" , "worker")
buildDockerImage.dependsOn(copyGeneratedTar)
assemble.dependsOn(buildDockerImage)
```
