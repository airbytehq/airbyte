# Saving Slack Messages

## Overview

The [slack free-tier](https://slack.com/pricing/paid-vs-free) saves only the last 10K messages. For social Slack instances, it may be impractical to upgrade to a paid plan to retain these message. Similarly, for an OSS project like Airbyte where we interact with our community through a public slack instance, the cost of paying for a seat for every slack member is inhibitive.

Searching through old messages can be really helpful. For me, losing that history feels like some advanced form of memory loss. What was that funny thing that someone said about chicken tenders? This contributor question sounds familiar, haven't we seen it before? But you just can't remember!

This tutorial will show you how you can, for _free_, use Airbyte to save these message (even after Slack deletes them). It will also provide you a convenient way to search through them.

Specifically we will export messages from your slack instance into search engine called MeiliSearch. We will be focusing on getting this setup running from your local workstation. We will mention at the end how you can set up a more productionized version of this pipeline.

We want to make this process easy, so while we will link to some external documentation for further exploration, we will provide all the instructions you need here to get this up and running.

## Set up Airbyte

Make sure you have Docker and Docker Compose installed. Then run the following commands:

```text
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

If you run into any problems, feel free to check out our more extensive [getting started](../getting-started.md) for more help.

Once you see an Airbyte banner, the UI is ready to go at [http://localhost:8000/](http://localhost:8000/). You can set your user preferences and then you will be brought to a page that asks you to set up a source. In the next step we'll go over how to do that.


## Connect to Slack

In the Airbyte UI select Slack from the dropdown. We provide step-by-step instructions for setting up the Slack source in Airbyte [here](../integrations/sources/slack.md). These will walk you through how to complete the form on this page.

By the end of these instructions you should have created a Slack source in the Airbyte UI. The Airbyte app will now prompt you to set up a destination. Next, we will now walk through how to set up MeiliSearch.

## Set up MeiliSearch

First let's get MeiliSearch running on our workstation. MeiliSearch has extensive docs for [getting started](https://docs.meilisearch.com/learn/tutorials/getting_started.html#download-and-launch). For this tutorial, however, we will give you all the instructions you need to set up MeiliSearch using docker.

```bash
    docker run -it --rm \
        -p 7700:7700 \
        -v $(pwd)/data.ms:/data.ms \
        getmeili/meilisearch
```

That's it!

{% hint style="info" %}
MeiliSearch stores data in `$(pwd)/data.ms`, so if you prefer to store it somewhere else, just adjust this path.
{% endhint %}

## Connect to Airbyte to MeiliSearch

Head back to the Airbyte UI. It should still be prompting you to set up a destination. Select "MeiliSearch" from the dropdown. For the `host` field, if you are on mac set: `http://host.docker.internal:7700`. If you are on linux use `http://localhost:7700`. The `api_key` can be left blank.

## Set up replication

On the next page, you will be asked to select which streams of data you'd like to replicate. We recommend selecting all of them except "files" and "remote files" (you won't really be able to search them well in this search engine).

For frequency, we recommend daily.

## Search MeiliSearch

After the connection has been saved, Airbyte should start replicating the data immediately. If you ever want to force replication immediately, you can click "sync now". When the sync is done, you can sanity check that this is all working by making a search request to MeiliSearch.

```bash
curl 'http://localhost:7700/indexes/messages/search' --data '{ "q": "<search-term>" }'
```

For example, I have the following message in one of the message that I replicated `welcome to airbyte.`.

```bash
curl 'http://localhost:7700/indexes/messages/search' --data '{ "q": "welcome to" }'
# => {"hits":[{"_ab_pk":"7ff9a858_6959_45e7_ad6b_16f9e0e91098","channel_id":"C01M2UUP87P","client_msg_id":"77022f01-3846-4b9d-a6d3-120a26b2c2ac","type":"message","text":"welcome to airbyte.","user":"U01AS8LGX41","ts":"2021-02-05T17:26:01.000000Z","team":"T01AB4DDR2N","blocks":[{"type":"rich_text"}],"file_ids":[],"thread_ts":"1612545961.000800"}],"offset":0,"limit":20,"nbHits":2,"exhaustiveNbHits":false,"processingTimeMs":21,"query":"test-72"}
```

##  (Optional) Search via a UI

Making curl requests to search your Slack History is a little clunky, so we have modified the example UI that MeiliSearch provides in [their docs](https://docs.meilisearch.com/learn/tutorials/getting_started.html#integrate-with-your-project) to search through the Slack results.

Download (or copy and paste the contents of) this [html file](https://github.com/airbytehq/airbyte/tree/master/docs/tutorials/index.html) to your workstation. Then open it using a browser. You should now be able to write search terms in the search bar and gets results instantly!

## "Productionizing" Saving Slack History

You can find instructions for how to host Airbyte on various cloud platforms [here](../deploying-airbyte).

MeiliSearch provides documentation on how to host it on cloud platforms [here](https://docs.meilisearch.com/running-production/#a-quick-introduction).

If you want to use the UI mentioned in the section above we recommend statically hosting that on S3, GCS, or equivalent.
