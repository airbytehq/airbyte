# Locally testing your changes

![testing is fun and games until it blows up](../assets/docs/science-kid.jpg)

You can test any change you make to see how it will look in production

The processes are almost identical from local testing to production so
you can have a high degree of confidence in the results

```bash
# navigate to docusaurus
cd docusaurus
# install the packages to run docusaurus
yarn install
# compile the current state of airbyte-cloud/docs
# into the website and serve it at http://localhost:3000
yarn build && yarn serve
# control-c sends the SIGTERM command to the running process
# this is a common way to exit running shell applications
# to exit the running server use control-c
```

- If you encounter a build error there may be multiple causes but usually this is due to a broken link:
  - fix your broken links and the build should work
- look at the changes you made locally, if they look great commit and add a funny picture to the PR for karma (technically optional)

**important note**
if you run `yarn build && yarn serve` and make changes after that you will need to exit the server using `control-c` from the command line and then running the command `yarn build && yarn serve` again to see your new changes
