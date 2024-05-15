# Mac Installation

Now that you have Docker set up for Airbyte, you can proceed to installation. We recommend that Mac users use brew if it is available. This way, you can install `abctl` using the following commands: 

```bash
brew tap airbytehq/tap
brew install abctl
```

An alternate approach for Mac users not using brew is to download the latest version of abctl from the [releases page](https://github.com/airbytehq/abctl/releases) and run the following command:

```bash
./abctl local install
```

If you didn't use brew to install, you may need to use the finder and Open With > Terminal to run the `abctl` command. After this, you should be able to run the command from the terminal. Airbyte suggests mac users to use `brew` if it is available.

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

