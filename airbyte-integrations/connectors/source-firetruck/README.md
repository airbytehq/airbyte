# Oracle Source V2

------

## Running tests on Apple Silicon

Some tests rely on an [Oracle testcontainer](https://java.testcontainers.org/modules/databases/oraclefree/) which will not work out of the box on M1+ Macs.
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

Now that colima is up and running, simply running the `test` gradle task is not enough, because testcontainers and the programmatic docker API it uses don't know about colima.
Testcontainers will just try to talk to `/var/run/docker.sock` by default.
We can work around this by setting some environment variables:
```
DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock" \
  TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE="${HOME}/.colima/default/docker.sock" \
  TESTCONTAINERS_HOST_OVERRIDE="$(colima ls -j | jq -r '.address')" \
  TESTCONTAINERS_RYUK_DISABLED=true \
  gw test
```

This should now run everything smoothly, at least the second time onwards; on the first run several docker images will be pulled and this might cause the tests to flake.

Note that:
- the CDK tests also involve testcontainers, these don't require colima and should work one way or the other;
- we pass an IP address to `TESTCONTAINERS_HOST_OVERRIDE`, which is why we had specified the`--network-address` flag in `colima start` earlier;
- Ryuk is disabled, what this means is that killing the `gradle` process with Ctrl+C or `kill -9 $(pgrep gradle)` or whatever will leave any running testcontainers run indefinitely, check with `docker ps`.
