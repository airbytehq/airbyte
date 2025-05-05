# Oracle Source V2

------

This repo exists because we want to incubate the new CDK and source-oracle-v2 needs to be closed source, for now at least.
Also, as it turns out, there aren't actually many dependencies on what's already in [airbytehq/airbyte](https://github.com/airbytehq/airbyte), whatever was needed has simply been copied over.

The source code is written mainly in Kotlin with a smattering of Java.
The build system is maven.

## CI & CD

These are handled by two github workflows:
- The [maven-verify](.github/workflows/maven-verify.yml) CI workflow runs all tests and checks for every PR, including when one gets sent to the merge queue.
  When successful, the pull request gets squashed and pushed to the `main` branch.
  The merge queue only accepts one pull request at a time.
- The [maven-deploy](.github/workflows/maven-deploy.yml) CD workflow builds the CDK jars and uploads them to the [Airbyte MyCloudRepo maven repository](https://airbyte.mycloudrepo.io/public/repositories/airbyte-public-jars/io/airbyte/cdk2/) on each commit pushed to `main`.
  The workflow generates a unique version number based on the length of the commit history.
  The workflow uses this version number in the jars and poms and also in the git tag that it tags the pushed commit with.

Pull requests therefore should therefore leave the maven project versions unchanged at `2.0-SNAPSHOT`.

## Building on Linux

Do whatever the [maven-verify CI workflow](.github/workflows/maven-verify.yml) does.

## Building on Apple Silicon

### Java 21

The required java version is 21.
Check that this is what you have:
```
$ java -version
openjdk version "21.0.3" 2024-04-16
OpenJDK Runtime Environment Homebrew (build 21.0.3)
OpenJDK 64-Bit Server VM Homebrew (build 21.0.3, mixed mode, sharing)
$ /usr/libexec/java_home --verbose
Matching Java Virtual Machines (2):
    21.0.3 (arm64) "Homebrew" - "OpenJDK 21.0.3" /opt/homebrew/Cellar/openjdk/21.0.3/libexec/openjdk.jdk/Contents/Home
    17.0.10 (arm64) "Homebrew" - "OpenJDK 17.0.10" /opt/homebrew/Cellar/openjdk@17/17.0.10/libexec/openjdk.jdk/Contents/Home
/opt/homebrew/Cellar/openjdk/21.0.3/libexec/openjdk.jdk/Contents/Home
$ echo $JAVA_HOME
/opt/homebrew/Cellar/openjdk/21.0.3/libexec/openjdk.jdk/Contents/Home
```
If you're not seeing something similar to this, get java 21 whichever way you prefer:
- `brew install openjdk@21`
- `sdk install java 21.0.3-amzn`
- `wget https://corretto.aws/downloads/latest/amazon-corretto-21-aarch64-macos-jdk.pkg`

### Maven

I chose maven over gradle because:
1. our needs are quite simple so the xml tag salad isn't too bothersome,
2. maven's main drawback is the absence of incremental builds, but that's mitigated by the support for incremental compilation in the Kotlin compiler,
3. the enforcer plugin ensures there are no unexpected dependency versions on the classpath,
4. maven is more CI-friendly than gradle and the github CI workflow file is both simple and efficient at what it does.

Note that none of these motivations will outlive the incubation period.
There is no desire to supplant gradle.

This build requires a modern version of maven, like 3.9, and should be using java 21 also:
```
$ mvn --version
Apache Maven 3.9.7 (8b094c9513efc1b9ce2d952b3b9c8eaedaf8cbf0)
Maven home: /opt/homebrew/Cellar/maven/3.9.7/libexec
Java version: 21.0.3, vendor: Homebrew, runtime: /opt/homebrew/Cellar/openjdk/21.0.3/libexec/openjdk.jdk/Contents/Home
Default locale: en_CA, platform encoding: UTF-8
OS name: "mac os x", version: "14.5", arch: "aarch64", family: "mac"
```
If this isn't what you're seeing, `brew install maven` or `brew upgrade maven`, and check the value of `$JAVA_HOME` because that's what maven uses.
Doing `rm -rf ~/.m2` as a prereq can't hurt either.

Once `mvn --version` succeeds, in the root of the repo do:
- `mvn clean validate` a couple of times, to check that it's processing the `pom.xml` files correctly and is able to download some plugins,
- `mvn package -DskipTests` a couple of times to compile all sources and test sources
- again, the first time it's run it will output a ton of noise because it's downloading plugins and dependencies into `~/.m2`.
- `mvn test` should run, but fail, this is expected on Mac, see below.

## Docker

The source-oracle-v2 tests rely on an [Oracle testcontainer](https://java.testcontainers.org/modules/databases/oraclefree/) which will not work out of the box on M1+ Macs.
This is because the [docker image](https://hub.docker.com/r/gvenzl/oracle-free) that this uses only works on x86-64 architectures.
Although Docker Desktop does provide some kind of VM (Rosetta) to emulate other platforms it won't work with this image.
The workaround involves installing and using [colima](https://github.com/abiosoft/colima) which runs the docker container in QEMU.
Visit the previous link for installation instructions.
For brew, it's `brew install colima`, and if you already have colima installed, `brew upgrade colima`.
Also, `colima delete` won't hurt.

Once colima is installed, we need to run it with an abundance of resources because Oracle is very hungry:
```
$ colima start --foreground --arch x86_64 --cpu 4 --memory 8 --disk 256 --network-address
```
Also, tell the docker client to use colima in preference to Docker Desktop or whatever regular docker server we'd be using otherwise:
```
$ docker context use colima
```
At this point, `docker ps` or `docker images` should report nothing, or not much, and:
```
$ docker context list
NAME                TYPE                DESCRIPTION                               DOCKER ENDPOINT                                      KUBERNETES ENDPOINT   ORCHESTRATOR
colima *            moby                colima                                    unix:///Users/postamar/.colima/default/docker.sock                         
default             moby                Current DOCKER_HOST based configuration   unix:///var/run/docker.sock                                                
desktop-linux       moby                Docker Desktop                            unix:///Users/postamar/.docker/run/docker.sock                             
```

Now that colima is up and running, simply running `mvn test` is not enough, because testcontainers and the programmatic docker API it uses don't know about colima.
Testcontainers will just try to talk to `/var/run/docker.sock` by default.
We can work around this by setting some environment variables:
```
DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock" \
  TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE="${HOME}/.colima/default/docker.sock" \
  TESTCONTAINERS_HOST_OVERRIDE="$(colima ls -j | jq -r '.address')" \
  TESTCONTAINERS_RYUK_DISABLED=true \
  mvn test
```

This should now run everything smoothly, at least the second time onwards; on the first run several docker images will be pulled and this might cause the tests to flake.

Note that:
- the CDK tests also involve testcontainers, these don't require colima and should work one way or the other;
- we pass an IP address to `TESTCONTAINERS_HOST_OVERRIDE`, which is why we had specified the`--network-address` flag in `colima start` earlier;
- Ryuk is disabled, what this means is that killing the `mvn` process with Ctrl+C or `kill -9 $(pgrep mvn)` or whatever will leave any running testcontainers run indefinitely, check with `docker ps`.
