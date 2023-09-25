# Deploy Airbyte

Deploying Airbyte Open-Source just takes two steps.

1. Install Docker on your workstation \(see [instructions](https://www.docker.com/products/docker-desktop)\). Make sure you're on the latest version of `docker-compose`.
2. Run the following commands in your terminal:

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
./run-ab-platform.sh 
```

Once you see an Airbyte banner, the UI is ready to go at [http://localhost:8000](http://localhost:8000)! You will be asked for a username and password. By default, that's username `airbyte` and password `password`. Once you deploy airbyte to your servers, **be sure to change these** in your `.env` file.

Alternatively, if you have an Airbyte Cloud invite, just follow [these steps.](../deploying-airbyte/on-cloud.md)

If you need direct access to our team for any kind of assistance, don't hesitate to [talk to our team](https://airbyte.com/talk-to-sales-premium-support) to discuss about our premium support offers.

## FAQ

If you have any questions about the Airbyte Open-Source setup and deployment process, head over to our [Getting Started FAQ](https://github.com/airbytehq/airbyte/discussions/categories/questions) on our Airbyte Forum that answers the following questions and more:

- How long does it take to set up Airbyte?
- Where can I see my data once I've run a sync?
- Can I set a start time for my sync?

If there are any questions that we couldn't answer here, we'd love to help you get started. [Join our Slack](https://airbytehq.slack.com/ssb/redirect) and feel free to ask your questions in the \#getting-started channel.
