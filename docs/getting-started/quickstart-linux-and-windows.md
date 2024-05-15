---
displayed_sidebar: docs
---

# Linux and Windows Installation

After getting Docker Windows set up for running Airbyte on your machine, download the latest version of abctl from the [releases page](https://github.com/airbytehq/abctl/releases) and run the following command:

```bash
./abctl local install
```

- Your browser should open to the Airbyte Application, if it does not visit [http://localhost](http://localhost)
- A prompt will ask for a username and password. By default, the username is`airbyte` and the password is `password`. You can set these values through command line flags or environment variables. For example, to set the username and password to `foo` and `bar` respectively, you can run the following command:

```bash
./abctl local install --username foo --password bar

# Or as Environment Variables
ABCTL_LOCAL_INSTALL_PASSWORD=foo
ABCTL_LOCAL_INSTALL_USERNAME=bar
```
The next time you want this local instance of Airbyte, just navigate to your installation and run the following: 

```bash
./run-ab-platform.sh
```

- Now you're ready to start moving some data!