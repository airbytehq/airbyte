Author: Augustin Lafanechere

Date: 2023-09-08

# What is this?
This notebook contains an analysis of our certified python connectors Dockerfile.
We originally had a lot of false certitudes that all our Python connectors are built the same.
This is an attempt at analyzing how similar, and different, our connector images are.

# Context
The Connector Operations team wants to consolidate our Python connector build process to have a single way of building connector images. This will be achieved via:
- the definition of a common base image which will contain the majority of the system needs of our connectors
- the definition of a common build procedure for our Python connectors (no per connector Dockerfile, we'll remove them)
- the definition of a simple framework of hooks that will allow connector developers to customize the connector image **only if needed**

# Worfklow
1. Determine the Dockerfile variants we have: scan our certified connectors dockerfile and identify families (variant) of Dockerfile that exists in our codebase. This will hopefully help us narrow down the analysis to a reduce number of images instead of analyzing all our connector images.
2. Analyze the different python base image use by the variants.
3. Analyze the environments variable set in these variants: we'll check which env var is common and static for all connectors, which env var common to all images but with different values and which env var is set on only a portion of Dockerfiles.
4. Analyze the system dependencies installed in the variants: assess if any connector is installing a custom system dependency and if we should make this dependency join the base image.
5. Given the conclusion of the previous steps, suggest a base image defintion and a build procedure for certified Python connectors.

# Let's code!


```python
from pathlib import Path
import pandas as pd
from connector_ops.utils import ConnectorLanguage, get_all_connectors_in_repo, Connector
import os
import git
import hashlib
import sys
import anyio
import dagger
# Changing current working directory to airbyte repo root
os.chdir(Path(git.Repo(search_parent_directories=True).working_tree_dir))
```


```python
ALL_CONNECTORS = get_all_connectors_in_repo()
```

## Identifying dockerfile variants
The function below parses the connectors dockerfiles and tries to remove the connector specifics instructions to determine a "variant". This will help us identify the different kind (variant) of Dockerfile existing in our codebase, instead of analysing each Dockerfile separatly. It will help narrow down our analysis.


```python
def get_dockerfile_variant(connector):
    dockerfile = Path(connector.code_directory / "Dockerfile").read_text()
    dockerfile = dockerfile.replace(connector.technical_name, "connector-technical-name")
    dockerfile = dockerfile.replace(connector.technical_name.replace("-", "_"), "connector_technical_name")

    for line in dockerfile.splitlines():
        # Remove dockerfile comments
        if line.startswith("#"):
            dockerfile = dockerfile.replace(line, "")
        # Remove connnector version label
        if line.startswith("LABEL io.airbyte.version"):
            dockerfile = dockerfile.replace(line, "")
    # Remove empty lines
    dockerfile = "\n".join([line for line in dockerfile.split("\n") if line.strip() != ""])
    # Remove extra spaces
    dockerfile = "\n".join([line.strip() for line in dockerfile.split("\n")])


    return hashlib.sha256(dockerfile.encode()).hexdigest()[:7]
```


```python
def get_connectors_for_analysis(languages, support_levels):
    return pd.DataFrame([
        {
            "dockerfile_variant": get_dockerfile_variant(c), 
            "technical_name": c.technical_name, 
            "support_level": c.support_level,
            "docker_image": f'{c.metadata["dockerRepository"]}:{c.metadata["dockerImageTag"]}',
            "dockerfile_path": Path(c.code_directory / "Dockerfile")
        }  for c in ALL_CONNECTORS if c.language in languages and c.support_level and c.support_level in support_levels
    ])
```


```python
SELECTED_SUPPORTS_LEVELS = ("certified")
SELECTED_LANGUAGES = (ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE)
CONNECTORS_FOR_ANALYSIS = get_connectors_for_analysis(SELECTED_LANGUAGES, SELECTED_SUPPORTS_LEVELS)
f"{len(CONNECTORS_FOR_ANALYSIS)} connectors selected for analysis"
```




    '47 connectors selected for analysis'




```python
DOCKERFILE_VARIANTS = CONNECTORS_FOR_ANALYSIS.groupby("dockerfile_variant").agg(dockerfile_example=("dockerfile_path", "first"), docker_image_example=("docker_image", "first"), total_count=("dockerfile_variant", "size")).sort_values("total_count", ascending=False)
print(f"Found {len(DOCKERFILE_VARIANTS)} Dockerfile variants")

```

    Found 14 Dockerfile variants


**We have identified **14** variants of Dockerfiles among our certified connectors.**

The rest of this analysis aims at:
- identifying the differences between these variants
- understanding the reason of these differences
- deciding whether these differences should be consolidated inside the future python base image

### Showing the **top 3 variants**:


```python
for i, example in enumerate(DOCKERFILE_VARIANTS[:3]["dockerfile_example"]):
    print(f"# -----VARIANT {i + 1}-----")
    print(example.read_text())

```

    # -----VARIANT 1-----
    FROM python:3.9-slim
    
    # Bash is installed for more convenient debugging.
    RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
    
    WORKDIR /airbyte/integration_code
    COPY source_instagram ./source_instagram
    COPY main.py ./
    COPY setup.py ./
    RUN pip install .
    
    ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
    ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
    
    LABEL io.airbyte.version=1.0.11
    LABEL io.airbyte.name=airbyte/source-instagram
    
    # -----VARIANT 2-----
    FROM python:3.9.11-alpine3.15 as base
    
    # build and load all requirements
    FROM base as builder
    WORKDIR /airbyte/integration_code
    
    # upgrade pip to the latest version
    RUN apk --no-cache upgrade \
        && pip install --upgrade pip \
        && apk --no-cache add tzdata build-base
    
    
    COPY setup.py ./
    # install necessary packages to a temporary folder
    RUN pip install --prefix=/install .
    
    # build a clean environment
    FROM base
    WORKDIR /airbyte/integration_code
    
    # copy all loaded and built libraries to a pure basic image
    COPY --from=builder /install /usr/local
    # add default timezone settings
    COPY --from=builder /usr/share/zoneinfo/Etc/UTC /etc/localtime
    RUN echo "Etc/UTC" > /etc/timezone
    
    # bash is installed for more convenient debugging.
    RUN apk --no-cache add bash
    
    # copy payload code only
    COPY main.py ./
    COPY source_notion ./source_notion
    
    ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
    ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
    
    LABEL io.airbyte.version=1.1.2
    LABEL io.airbyte.name=airbyte/source-notion
    
    # -----VARIANT 3-----
    FROM python:3.9-slim
    
    # Bash is installed for more convenient debugging.
    RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*
    
    WORKDIR /airbyte/integration_code
    COPY setup.py ./
    RUN pip install .
    COPY source_twilio ./source_twilio
    COPY main.py ./
    
    ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
    ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
    
    LABEL io.airbyte.version=0.10.0
    LABEL io.airbyte.name=airbyte/source-twilio
    


### Conclusions after reading the top 3 Dockerfile variants
* The base image used are slightly differents: `python:3.9-slim` and `python:3.9.11-alpine3.15`
* Variant 1 and 3 are not explicitely setting the system timezone to UTC. Variant 2 is.
* Variant 2 is using a multi stage build that can improve build speed and image size
* Vairant 1 and 3 are pretty similar but have a different approach at installing the connector python package. Variant 3 copies `setup.py` in a specific layer to cache dependency install. Variant 3 is better than variant 1 for build speed.

**Takeaways for building our future base image:**
1. We should explicitely set the timezone to UTC on it
2. We should leverage dependency install caching with smart docker layering
3. The multi-staging operations can be reproduced in Dagger via the creation of multiple containers (one per stage) and exchange of their filesytems with `with_directory` instructions.

## Base images analysis


```python
all_base_images = {example.read_text().splitlines()[0].replace(" as base", "").replace("FROM ", "") for example in DOCKERFILE_VARIANTS["dockerfile_example"]}
all_base_images
```




    {'python:3.9-slim',
     'python:3.9.11-alpine3.15',
     'python:3.9.11-slim',
     'python:3.9.16-alpine3.18'}



### Conclusion
We are using 4 different Python base image in our certified connectors:
* python:3.9-slim
* python:3.9.11-slim
* python:3.9.11-alpine3.15
* python:3.9.16-alpine3.18

The most concerning difference is the fact we have `slim` and `alpine` images. 
The use of the `alpine` images can be explained by the willingness of optimizating the image size.  
But some connector depends on Python packages like NumPy that do not work well under `alpine` because of the lack of some system dependencies, hence the use of the `slim` images.

**Takeaways for building our future base image:**

**I suggest using a broad image like `python:3.9.18-bookworm` as the base of our base image as it will guarantee:**
* That we are running the latest python 3.9 version
* That we have a maximum of system packages that some connector dependencies might need

It is best for maintenance and consolidation,  not optimal for image size: but image size is not something we're currently trying to optimize.

## Environment variables analysis

### Retrieving the env vars set in our 14 variants
1. Pull connector image corresponding to each variant
2. Call `printenv` on each image
3. Gather results in a list of env vars per variant


```python
docker_variants_env_vars = []
async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
    for connector_image in DOCKERFILE_VARIANTS["docker_image_example"]:
        printenv_output = await dagger_client.container().from_(connector_image).with_exec(["printenv"], skip_entrypoint=True).stdout()
        env_vars = {}
        for env_var in printenv_output.splitlines():
            k, v = env_var.split("=")
            env_vars[k] = v
        docker_variants_env_vars.append(env_vars)


```

### Environment variables with values common to all images


```python
def get_common_env_vars_values(env_vars_per_variant):
    tuplized_kv = [{(k,v) for k, v in variant.items()} for variant in env_vars_per_variant]
    common_env_var_values = tuplized_kv[0]

    for env_var_set in tuplized_kv[1:]:
        common_env_var_values = common_env_var_values.intersection(env_var_set)
    return pd.DataFrame(common_env_var_values, columns=["Env var name", "Env var value"])

    
common_env_var_values = get_common_env_vars_values(docker_variants_env_vars)
common_env_var_values
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Env var name</th>
      <th>Env var value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>LANG</td>
      <td>C.UTF-8</td>
    </tr>
    <tr>
      <th>1</th>
      <td>PYTHON_SETUPTOOLS_VERSION</td>
      <td>58.1.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>HOME</td>
      <td>/root</td>
    </tr>
    <tr>
      <th>3</th>
      <td>PATH</td>
      <td>/usr/local/bin:/usr/local/sbin:/usr/local/bin:...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>OTEL_TRACES_EXPORTER</td>
      <td>otlp</td>
    </tr>
    <tr>
      <th>5</th>
      <td>GPG_KEY</td>
      <td>E3FF2839C048B25C084DEBE9B26995E310250568</td>
    </tr>
    <tr>
      <th>6</th>
      <td>OTEL_EXPORTER_OTLP_TRACES_ENDPOINT</td>
      <td>unix:///dev/otel-grpc.sock</td>
    </tr>
    <tr>
      <th>7</th>
      <td>OTEL_EXPORTER_OTLP_TRACES_PROTOCOL</td>
      <td>grpc</td>
    </tr>
  </tbody>
</table>
</div>



**Takeaways for building our future base image:**

This list of static env var is interesting to know as it will allow us to write tests on our future connector images that will check that:
- these env var are set
- these env var values are always with the same values

These env vars are not set on our Dockerfiles and are  coming from the Python base image: 


```python
async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
    for base_image in all_base_images:
        base_image_container = dagger_client.container().from_(connector_image)
        base_env_vars_raw = (await base_image_container.with_exec(["printenv"], skip_entrypoint=True).stdout()).splitlines()
        base_env_vars = {}
        for base_env_var in base_env_vars_raw:
            k, v = base_env_var.split("=")
            base_env_vars[k] = v
        for _, common_env_var in common_env_var_values.iterrows():
            assert base_env_vars[common_env_var["Env var name"]] == common_env_var["Env var value"]
   
        
```

### Environment variables common to all images but with different values


```python
def get_common_env_vars(env_vars_per_variant):
    env_var_keys_per_variant = [set(variant.keys()) for variant in env_vars_per_variant]
    common_env_var = env_var_keys_per_variant[0]

    for env_var_set in env_var_keys_per_variant[1:]:
        common_env_var = common_env_var.intersection(env_var_set)
    return pd.Series(list(common_env_var))

    
common_env_var = get_common_env_vars(docker_variants_env_vars)
common_env_var_key_different_values = set(common_env_var) - set(common_env_var_values["Env var name"])
common_env_var_key_different_values
```




    {'AIRBYTE_ENTRYPOINT',
     'OTEL_TRACE_PARENT',
     'PYTHON_GET_PIP_SHA256',
     'PYTHON_GET_PIP_URL',
     'PYTHON_PIP_VERSION',
     'PYTHON_VERSION',
     'TRACEPARENT'}




```python
def get_unique_values_for_env_vars(docker_variants_env_vars):
    unique_values_for_env_vars = {}
    for docker_variant_env_vars in docker_variants_env_vars:
        for k, v in docker_variant_env_vars.items():
            if k not in unique_values_for_env_vars:
                unique_values_for_env_vars[k] = set()
            unique_values_for_env_vars[k].add(v)
    return unique_values_for_env_vars
```

#### Differences in `AIRBYTE_ENTRYPOINT`
Differences in `AIRBYTE_ENTRYPOINT` are not expected. We want all python connector to have it set to `python /airbyte/integration_code/main.py`.  

A single connector, `source-zendesk-chat`, has its entrypoint set to `python /airbyte/integration_code/main_dev.py`. It looks like a legacy thing that we should correct. But as the base image project is not targetted at fixing connectors we'll handle this custom env var with a post build hook.


```python
get_unique_values_for_env_vars(docker_variants_env_vars)["AIRBYTE_ENTRYPOINT"]
```




    {'python /airbyte/integration_code/main.py',
     'python /airbyte/integration_code/main_dev.py'}



#### Differences in `PYTHON_VERSION`
All certified connectors are running Python 3.9 but with subtle differences in the patch version:
* 3.9.18
* 3.9.17
* 3.9.16
* 3.9.11

This can be explained the use of `python:3.9-slim` base image tag. This tag is updated to the latest python 3.9 version when a new version get released. Some connectors that had not been built for a while can stay behind the latest Python 3.9 version until they're not rebuilt.
Another reason for this difference is that some connector use `python:3.9.11-slim` which is pinning Python 3.9.11.
For **reproductible built** our base image will be based on a `sha256` docker tag, it will make sure we're always using the same image as a base.


```python
different_python_version = get_unique_values_for_env_vars(docker_variants_env_vars)["PYTHON_VERSION"]
print(f"Different Python version in use: {', '.join(different_python_version)}")
```

    Different Python version in use: 3.9.17, 3.9.11, 3.9.16


#### Differences in `PYTHON_PIP_VERSION`
Two different `pip` version are in used in our connectors:
* 23.0.1
* 22.0.4

This can be explained by:
* The use of different base images that might bundle different pip version
* The `pip install --upgrade pip` instruction in our Dockerfile that might upgrade `pip` on rebuild of the image

**Takeaways for building our future base image:**
For reproductible build we likely want to pin the pip version. 
This will be naturaly achieved by using a static base python image which comes with pip pre-installed.
If we want to use a custom pip version we should pin it by running `pip install pip==<pip-version>` in our future base image.


```python
different_pip_version = get_unique_values_for_env_vars(docker_variants_env_vars)["PYTHON_PIP_VERSION"]
print(f"Different Python Pip version in use: {', '.join(different_pip_version)}")
```

    Different Python Pip version in use: 22.0.4, 23.0.1


#### Differences in `PYTHON_GET_PIP_URL`, `PYTHON_GET_PIP_SHA256`
We have 4 different value for these env vars.
This matches the 4 different Python images we use:
These env var are probably set at build time of the python base images and match a version of the `pip` installation script.

**Takeaways for building our future base image:**
As we'll use a single base image for all certified connectors, this base image will be built on a base python image: all our connector will have the same value for these env vars. No action needed.


```python
get_unique_values_for_env_vars(docker_variants_env_vars)["PYTHON_GET_PIP_SHA256"]
```




    {'394be00f13fa1b9aaa47e911bdb59a09c3b2986472130f30aa0bfaf7f3980637',
     '45a2bb8bf2bb5eff16fdd00faef6f29731831c7c59bd9fc2bf1f3bed511ff1fe',
     '96461deced5c2a487ddc65207ec5a9cffeca0d34e7af7ea1afc470ff0d746207',
     'e235c437e5c7d7524fbce3880ca39b917a73dc565e0c813465b7a7a329bb279a'}




```python
get_unique_values_for_env_vars(docker_variants_env_vars)["PYTHON_GET_PIP_URL"]
```




    {'https://github.com/pypa/get-pip/raw/0d8570dc44796f4369b652222cf176b3db6ac70e/public/get-pip.py',
     'https://github.com/pypa/get-pip/raw/38e54e5de07c66e875c11a1ebbdb938854625dd8/public/get-pip.py',
     'https://github.com/pypa/get-pip/raw/9af82b715db434abb94a0a6f3569f43e72157346/public/get-pip.py',
     'https://github.com/pypa/get-pip/raw/d5cb0afaf23b8520f1bbcfed521017b4a95f5c01/public/get-pip.py'}



#### Differences in `TRACEPARENT` and `OTEL_TRACE_PARENT`
On these env var we have a different value for each connector image.
I believe these are set at build time by the Docker engine.
These Ids can be used for tracing. I don't know if they are actively use in our current infrastructure.

**Takeaways**:
On connector build in `airbyte-ci` we should verify that these env var are set.


```python
get_unique_values_for_env_vars(docker_variants_env_vars)["TRACEPARENT"]
```




    {'00-05babbaa467d2b7101a1c3c4b75c1b5f-dd8adab127d27f39-01',
     '00-15262d0156d304755c1a37aab7400d91-d000781658986ada-01',
     '00-492c7d03978cbd27941a0f01c64d0ea2-53174fa4a8f396d5-01',
     '00-4cfe6e40354d22eef1c8bd44a53de77b-c791eac4904fd1f2-01',
     '00-5a8d6c04188be1aebce946a1ef5e61a2-52f2d30a2ae782ed-01',
     '00-624b92c81c4de6a0f0f8e7bdee0e3ba3-0ab1ead787e1426b-01',
     '00-659529510ea31fffdb43e578b7a61e85-3274b696e496d0d2-01',
     '00-7cd60817e3b3542b6bd91c22098ff33a-03a4d5e08021248d-01',
     '00-9d69486c8f84d271449e4885eec67943-7c2a3f817dbca68b-01',
     '00-a215dd2bf43039a9f04c28219a7cb5e9-5c12bf9a7651cfba-01',
     '00-af060a2eb1bd83b31d40d0da6232e6e1-d1e86c8724866a37-01',
     '00-caf0d2479373ae86133704e4e2f19e73-3536098ec356a6c0-01',
     '00-fca418ed06415f3741ff550a232cf257-0216c5a3245cbf48-01',
     '00-fff1fd9d58a2ba8c407a0ee94c965aa5-eafd1f6498b40fac-01'}




```python
get_unique_values_for_env_vars(docker_variants_env_vars)["OTEL_TRACE_PARENT"]
```




    {'00-05babbaa467d2b7101a1c3c4b75c1b5f-dd8adab127d27f39-01',
     '00-15262d0156d304755c1a37aab7400d91-d000781658986ada-01',
     '00-492c7d03978cbd27941a0f01c64d0ea2-53174fa4a8f396d5-01',
     '00-4cfe6e40354d22eef1c8bd44a53de77b-c791eac4904fd1f2-01',
     '00-5a8d6c04188be1aebce946a1ef5e61a2-52f2d30a2ae782ed-01',
     '00-624b92c81c4de6a0f0f8e7bdee0e3ba3-0ab1ead787e1426b-01',
     '00-659529510ea31fffdb43e578b7a61e85-3274b696e496d0d2-01',
     '00-7cd60817e3b3542b6bd91c22098ff33a-03a4d5e08021248d-01',
     '00-9d69486c8f84d271449e4885eec67943-7c2a3f817dbca68b-01',
     '00-a215dd2bf43039a9f04c28219a7cb5e9-5c12bf9a7651cfba-01',
     '00-af060a2eb1bd83b31d40d0da6232e6e1-d1e86c8724866a37-01',
     '00-caf0d2479373ae86133704e4e2f19e73-3536098ec356a6c0-01',
     '00-fca418ed06415f3741ff550a232cf257-0216c5a3245cbf48-01',
     '00-fff1fd9d58a2ba8c407a0ee94c965aa5-eafd1f6498b40fac-01'}



### Connector specific environment variables
Some connector are setting custom environment variables.
#### `AIRBYTE_IMPL_MODULE` and `AIRBYTE_IMPL_PATH` 
These variables are [used in the CDK](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/entrypoint.py#L256) to override some default behavior in the connector entrypoint.  `source-zendesk-chat` is setting these env var. I can't assess if it's rightfully doing so. We'll support this by custom pre/post build hooks for this connector.

#### `CODE_PATH` and `WORKDIR`
`source-slack` is setting these two env vars. These are only used in the Dockerfile context and can likely be discarded as this logic will be declared with the common build process in `airbyte-ci`. :
```Dockerfile
ENV WORKDIR=/airbyte/integration_code

WORKDIR $WORKDIR

COPY setup.py ./
RUN pip install .

COPY $CODE_PATH ./$CODE_PATH
```


```python
for variant_env_vars in docker_variants_env_vars:
    for k, v in variant_env_vars.items():
        if k not in set(common_env_var):
            print(f"Connector specific env var: {k}={v}")
```

    Connector specific env var: CODE_PATH=source_slack
    Connector specific env var: WORKDIR=/airbyte/integration_code
    Connector specific env var: CODE_PATH=source_zendesk_chat
    Connector specific env var: AIRBYTE_IMPL_MODULE=source_zendesk_chat
    Connector specific env var: AIRBYTE_IMPL_PATH=SourceZendeskChat


## Custom system dependencies analysis


```python

async def get_installed_system_packages(container, dagger_client):
    try:
        output = await container.with_exec(["dpkg", "--get-selections"], skip_entrypoint=True).stdout()
    except dagger.ExecError:
        # Use apk info for alpine
        output =  await container.with_exec(["apk", "info", "-q"], skip_entrypoint=True).stdout()
    return set(output.replace("\t", "").replace("install", "").splitlines())

docker_variants_env_vars = []
base_pkgs = set()
images_with_custom_pkgs = set()
async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
    for base_image in all_base_images:
        base_image_container = dagger_client.container().from_(base_image)
        base_pkgs.update(await get_installed_system_packages(base_image_container, dagger_client))
    for connector_image in DOCKERFILE_VARIANTS["docker_image_example"]:
        connector_image_container = dagger_client.container().from_(connector_image)
        connector_image_pkgs = await get_installed_system_packages(connector_image_container, dagger_client)
        custom_pkgs = connector_image_pkgs - base_pkgs
        if custom_pkgs:
            print(f"{connector_image} is installing custom system packages: {', '.join(custom_pkgs)}")
            images_with_custom_pkgs.add(connector_image)


```

    airbyte/source-instagram:1.0.11 is installing custom system packages: libcrypt-dev:arm64, libtirpc-dev:arm64, libc6-dev:arm64, rpcsvc-proto, libnsl-dev:arm64, linux-libc-dev:arm64, libc-dev-bin
    airbyte/source-twilio:0.10.0 is installing custom system packages: libcrypt-dev:arm64, libtirpc-dev:arm64, libc6-dev:arm64, rpcsvc-proto, libnsl-dev:arm64, linux-libc-dev:arm64, libc-dev-bin
    airbyte/source-gitlab:1.6.0 is installing custom system packages: libcrypt-dev:arm64, libtirpc-dev:arm64, libc6-dev:arm64, rpcsvc-proto, libnsl-dev:arm64, linux-libc-dev:arm64, libc-dev-bin
    airbyte/source-google-analytics-v4:0.2.1 is installing custom system packages: libcrypt-dev:arm64, libtirpc-dev:arm64, libc6-dev:arm64, rpcsvc-proto, libnsl-dev:arm64, linux-libc-dev:arm64, libc-dev-bin
    airbyte/source-salesforce:2.1.4 is installing custom system packages: libcrypt-dev:arm64, libtirpc-dev:arm64, libc6-dev:arm64, rpcsvc-proto, libnsl-dev:arm64, linux-libc-dev:arm64, libc-dev-bin


**The images listed above have extra system packages compared to there base image. But no instruction in the dockerfile installs these system packages. My current hypothesis is that the base image they use had these system packages in previous versions. Let's rebuild these connector and see if the "custom packages" are still there.**


```python
async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
    for connector_image in images_with_custom_pkgs:
        connector = Connector(connector_image.split(":")[0].replace("airbyte/", ""))
        connector_container = dagger_client.host().directory(str(connector.code_directory)).docker_build()
        connector_container_pkgs = await get_installed_system_packages(connector_container, dagger_client)
        custom_pkgs = connector_container_pkgs - base_pkgs
        assert not custom_pkgs
        print(f"No custom packages found after local build of {connector}")
```

    No custom packages found after local build of source-instagram
    No custom packages found after local build of source-twilio
    No custom packages found after local build of source-gitlab
    No custom packages found after local build of source-google-analytics-v4
    No custom packages found after local build of source-salesforce


#### Takeaways for the future base image

1. We don't have any certified python connector that is installing a custom system dependency
2. The use of base images tag that can change the underlying image in use (like python3.9-slim: it might get updated on each patch version of python 3.9) proves again that we can't achieve reproductible build with these images. We should definitely be targetting tag with their `sha256`: e.g `python:3.9@sha256:0596c508fdfdf28fd3b98e170f7e3d4708d01df6e6d4bffa981fd6dd22dbd1a5`. This will ensure that on rebuild the same base image will be used.


# Overall analysis conclusion
### Base images to use for our base image:
We want to use a python image with 3.9 in its latest patch versio,: 3.9.18
We want to use debian as it has proven its good fit for our existing connector image.
We want to use a debian image that has a maximum of system package to avoid connector specific package install: let's use `bullseye`, the latest debian version release name.
[python:3.9.18-bullseye](https://hub.docker.com/layers/library/python/3.9.18-bullseye/images/sha256-d7e28b2648cb4611a94f068d92a236e7faaf6edb7589e01c09c1c16035c26d0a?context=explore)
- For AMD64: `python:3.9.18-bullseye@sha256:d7e28b2648cb4611a94f068d92a236e7faaf6edb7589e01c09c1c16035c26d0a`
- For AMR64: `python:3.9.18-bullseye@sha256:a3fc5f7523dbda93d333b6d98704691acf1a921b5cca89206452d5d31a717beb`

### System settings to set on our base image:
We must set the timezone to UTC

### Environment variable that must exists on our connector images
#### Common env vars with static values (check the specific section for values)
- `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`
- `GPG_KEY`
- `LANG`
- `PATH`
- `PYTHON_SETUPTOOLS_VERSION`
- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`
- `OTEL_TRACES_EXPORTER`
- `HOME`
- `PYTHON_VERSION`
- `PIP_VERSION`
- `PYTHON_GET_PIP_SHA256`
- `PYTHON_GET_PIP_URL`
  
This env vars will likely be set by the python base image we'll use. But we must add a test that ensure they are set, to avoid any regression on new connector versions.

#### Common env vars with custom values
- `AIRBYTE_ENTRYPOINT`: this should default to `python /airbyte/integration_code/main.py` but `source-zendesk-chat` has set it to `python /airbyte/integration_code/main_dev.py` (we should handle this edge case with pre/post build hook).
- `OTEL_TRACE_PARENT` and `TRACEPARENT`: We believe these are set at build time by the docker engine, but we should make sure our dagger build still set these (or understand there purpose)

#### Custom env vars
- `AIRBYTE_IMPL_MODULE` and `AIRBYTE_IMPL_PATH`: These are set by `source-zendesk-chat`, we must implement a pre/post build hook for this connector to set these env var at build time.

### System packages dependencies
No certified connector is installing a custom system dependency.
The system packages bundled with the python base image I suggest to use should guarantee all system requirements are met for all our connectors.

### Labels
All our connector image set the following labels. We should continue to use these, but I'm not sure of there actual usefulness.
```Dockerfile
LABEL io.airbyte.version=<semver-connector-version>
LABEL io.airbyte.name=airbyte/<connector-technical-name>
```

# Next steps
1. Declare a first base image version in a new python package under `airbyte-ci/connectors/base_images/`
2. Declare a common build procedure for connector images in `airbyte-ci/connectors/pipelines`
3. Implement a light pre/build hook framework to customize connector build process if needed

A "prototype" of these steps is available in [this PR](https://github.com/airbytehq/airbyte/pull/29477/files). This PR has not been yet updated to capture the conclusion of this analysis.
