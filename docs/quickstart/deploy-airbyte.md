# Deploy Airbyte

* Install Docker on your workstation \(see [instructions](https://www.docker.com/products/docker-desktop)\). Note: There is a known issue with docker-compose 1.27.3. If you are using that version, please upgrade to 1.27.4.
* After Docker is installed, you can immediately get started locally by running:

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

* Once you see an Airbyte banner, the UI is ready to go at [http://localhost:8000](http://localhost:8000)!

## FAQ

If you have any questions about the Airbyte setup and deployment process, head over to our [Getting Started FAQ](../faq/getting-started.md) that answers the following questions and more:

- How long does it take to set up Airbyte?
- Where can I see my data once I've run a sync?
- Can I set a start time for my sync?

If there are any questions that we couldn't answer here, we'd love to help you get started. [Join our Slack](https://airbytehq.slack.com/ssb/redirect) and feel free to ask your questions in the #getting-started channel.
