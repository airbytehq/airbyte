import pandas as pd
import requests

from dagster import MetadataValue, Output, asset


@asset
def hackernews_top_story_ids():
    """
    Get top stories from the HackerNews top stories endpoint.
    API Docs: https://github.com/HackerNews/API#new-top-and-best-stories
    """
    top_story_ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    ).json()
    return top_story_ids[:10]


# asset dependencies can be inferred from parameter names
@asset
def hackernews_top_stories(hackernews_top_story_ids):
    """Get items based on story ids from the HackerNews items endpoint"""
    results = []
    for item_id in hackernews_top_story_ids:
        item = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        ).json()
        results.append(item)

    df = pd.DataFrame(results)

    # recorded metadata can be customized
    metadata = {
        "num_records": len(df),
        "preview": MetadataValue.md(df[["title", "by", "url"]].to_markdown()),
    }

    return Output(value=df, metadata=metadata)
