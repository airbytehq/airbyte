This .md file is meant as (Swisscom) developer friendly version of to the destination-teradata/README.md - too succinct - guide.


# Setup your development pipeline for the "teradata-destination" connector
## known limitations
- This dev pipeline is not meant to pass through a proxy, it supposes full internet access from the developer's computer.
- if using a local teradata instance for integration tests: 
   you should have an x86 CPU architecture as virtualisation software for ARM does not work well 
(at least on MacOS: requires x86 emulation which is extremely slow)

## prerequisites
- python >=3.10 registered as "python" in the cli 
- docker(-desktop) process is running, accessible as "docker" in the cli
- "jq" json command-line processor is installed in the cli


## Install step 1: Airbyte-ci & dependencies
Airbyte-ci is a local-development utility underpinning the whole airbyte connectors Continuous Integration process: build, test, publish
It must be properly installed and setup

Start in your (shell) cli from the root of this airbyte git repository, then:
1) make tools.airbyte-ci.install    # Install airbyte-ci locally
2) export PATH="$HOME/.local/bin:$PATH" # Add this in your .zshrc/.bashrc to reference the airbyte-ci bin
3) Disable docker desktop proxy config (see ["Docker desktop without proxy config"](./README-swisscom-dev.md#Docker-desktop-without-proxy-config))
4) Make sure to have a reachable Teradata instance for integration tests (see [here]())
5) configure the destination-teradata ./secrets/secrets.json file to target the Teradata instance
   - Set the DB username, password, host, and jdbc_url
   - If using the local teradata VM, either set the VM's IP or localhost depending on the VM network setup
6) Run unit & integration tests in your cli
   ``` bash
    # disable-proxies
    export HTTP_PROXY="";
    export http_proxy="";
    export HTTPS_PROXY="";
    export  https_proxy="";
    # try run unit & integration tests
    airbyte-ci connectors --name=destination-teradata  test;
   ```

### Dependency: Docker desktop without proxy config
airbyte-ci is meant to operate with unfiltered/no-proxy access to internet.
You may try to pass through your company's proxy but it is not straightforward at all.
As a consequence, one needs to adapt the proxy setup in the docker config for integration tests to run smoothly

Adapt the docker config(s)
1) In the docker-desktop UI Settings>Resources>Proxies, Enable "Manual proxy configuration" and leave fields blank
2) restart docker desktop
3) make sure that (or enforce)  ~/.docker/config.json has "proxies" entry as follows:
   {
   "proxies": {"default": {}}
   }

### Dependency: Install a teradata VM as target
1) Install a VM software
   - Intel Silicon: Virtual box with "brew install --cask virtualbox"
   - ARM Silicon : UTM: https://mac.getutm.app/
2) Download the Teradata official VM image
   - The Teradata Vantage Express 17.10 VM image is available for download [here](https://downloads.teradata.com/download/database/teradata-express/vmware) 
   - You need a teradata account (easy to create) to download the official VM file.
3) Follow the relevant Teradata VM installation guide depending on th VM software you use:
   - For UTM [here](https://quickstarts.teradata.com/getting.started.utm.html#_overview) (Extremely slow but works for Mac-ARM silicon, must run in "x86" emulation mode)
      - Note: If you want to follow the guide for network, choose "Emulated VLAN" mode and then setup the necessary port forwarding as recommended in the setup guide
      - Tip: If you cannot connect from your host (intellij interactive DB client) to the VM with the guide-suggested network mode, 
             try "shared network" (default selection) : the VM will be seen by the host ads another computer with an individual ip and expose all its ports. 
             Then, in intellij, just specify the VM ip (use "ifconfig" in the vm cli to get the ip) for the teradata client 
                 (leave port empty (will fallback to default 1025) to avoid strange ipv6 parsing bug in java lib).
   - For VirtualBox [there](https://quickstarts.teradata.com/getting.started.vbox.html)
   - For VMware [over there](https://quickstarts.teradata.com/getting.started.vmware.html)
4) IMPORTANT: to gracefully stop Teradata and the VM run the following commands in the terminal:
     ``` bash
      tpareset -x "Stoping Teradata DB service before VM poweroff";
      poweroff;
    ```




## Install step 2: Setup airbyte connector project in intellij
The following assumes step 1 worked.

Integration tests are necessary to test the Teradata destination connector as a whole "blackbox" in isolation on the developer machine.
This enables shorter development cycles and debugging rather than building and publishing the code on the Airbyte platform without knowing if the expected basic functionality^ actually works.

Try running the acceptance test "TeradataDestinationAcceptanceTest.java" from Intellij.
When "executing" the test class, Gradle is supposed to prepare the necessary python orchestration environment on your machine before actually running the Java tests.
However, experience may be far from smooth for a Swisscom developer machine running with an ARM + MacOs + homebrew + proxy(to disable) setup.
In the following is a collection of tips to help you troubleshoot through this.
Trust me, "It (eventually) worked on my machine..."

### Documentation
- Acceptance Tests Reference [doc](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference)


### Tip: disable the proy - When running acceptance/integration tests, set env http proxy variables to empty strings
The airbyte connectors repo is meant to operate with unfiltered/no-proxy.
As a consequence, one needs to adapt the run configs for integration tests to run smoothly

In intellij's run config for the test make sure that "Environment variables" have empty strings for any proxy related setting:
HTTP_PROXY=;
http_proxy=;
HTTPS_PROXY=;
https_proxy=;
JAVA_OPTS : make sure that " -Djava.net.useSystemProxies, -Dhttp.nonProxyHosts" and any proxy related variable is not set
JAVA_HOME = //Path to java 21 JDK (may not be necessary, but to be sure)

### Tip: java version - When running tests, make sure you use the correct java 21 version for the whole Intellij project & Gradle build
Intellij project: file > project structure...> Project > Select "SDK" field to be java 21
Gradle settings in Intelij :  "settings" menu  > Build, Execution, deployment > build tools > "Gradle JVM" field select either java 21 or Project SDK 

### Tip: python virtualenv - If gradle-auto install does not work, manually install it
On MacOs, brew package manager may override python pip's ability to install machine-wide packages thus making the gradle based python setup failing.
Python's virtualenv must at least be setup properly by hand if the gradle-centric installation does not work:
1) cli > python -m pip install virtualenv --break-system-packages
2) in file: $gitProjectRoot/airbyte-integrations/connectors/build.gradle, add configs
   ..
   python {
   pythonPath = '/opt/homebrew/bin/' // path to your python 3.10
   virtualenvVersion = '20.26.2' // virtual env 20.26.x
   installVirtualenv = false // got manually installed by step 1)

### Tip: python package manager poetry - If poetry-based packages install does not work, manually install them
Follow the installation for development guidelines in the $gitProjectRoot/airbyte-ci/connectors/pipelines/README.md file

### Tip: running specific integration tests
Airbyte has a minimum set of standard integration tests that the destination connector test must pass to be compliant with the platform (See DestinationAcceptanceTest.java).
The specialised test class TeradataDestinationAcceptanceTest inherits and overrides some aspects of it.
