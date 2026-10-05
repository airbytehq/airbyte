# API Direct
Real-time public data from Twitter/X, Reddit, YouTube, Instagram, TikTok, Facebook, Threads, Bluesky, Truth Social, LinkedIn, Google Search, Google Maps, news sites, forums, Amazon and Trustpilot through API Direct (https://apidirect.io). Search streams run once per search term; account streams follow the usernames, pages and URLs you list. Pay per request with a free monthly tier per endpoint.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API key. Your API Direct key, which starts with ak_live_. Create a free account at https://apidirect.io/signup?utm_source=airbyte and copy a key from https://apidirect.io/dashboard/keys. |  |
| `queries` | `array` | Search terms. Keywords, brands or phrases to search for. Every search stream runs once per term per sync. Boolean syntax works where the endpoint supports it, see https://apidirect.io/docs/boolean-search. |  |
| `start_date` | `string` | Start date. Earliest publication date to sync on the incremental streams (YYYY-MM-DD, UTC). Defaults to 30 days before the first sync. |  |
| `pages` | `integer` | Pages per request. How many result pages to read per search term or account on each sync, up to each endpoint&#39;s limit. Every page is billed as one request, see https://apidirect.io/docs/pricing. | 1 |
| `country` | `string` | Country. Two-letter ISO 3166-1 country code for the web, news, forum and places streams, e.g. us or gb. Leave empty for each endpoint&#39;s default. |  |
| `language` | `string` | Language. Two-letter ISO 639-1 language code for the web, news and places streams, e.g. en. Leave empty for each endpoint&#39;s default. |  |
| `amazon_country` | `string` | Amazon marketplace. Marketplace country for the Amazon streams. Leave empty for us. |  |
| `twitter_usernames` | `array` | Twitter/X usernames. Accounts whose tweets, replies and profile to sync, without the @. | [] |
| `instagram_usernames` | `array` | Instagram usernames. Accounts whose posts and profile to sync. | [] |
| `tiktok_usernames` | `array` | TikTok usernames. Accounts whose profile to sync, without the @. | [] |
| `threads_usernames` | `array` | Threads usernames. Accounts whose posts and profile to sync. | [] |
| `bluesky_usernames` | `array` | Bluesky handles. Accounts whose posts and profile to sync, e.g. bsky.app. | [] |
| `truthsocial_usernames` | `array` | Truth Social usernames. Accounts whose posts to sync. | [] |
| `youtube_channel_urls` | `array` | YouTube channel URLs. Channels whose details to sync. | [] |
| `youtube_video_urls` | `array` | YouTube video URLs. Videos whose details and comments to sync. | [] |
| `facebook_page_urls` | `array` | Facebook page URLs. Pages whose details, posts and reviews to sync. | [] |
| `facebook_group_urls` | `array` | Facebook group URLs. Public groups whose details and posts to sync. | [] |
| `linkedin_company_urls` | `array` | LinkedIn company URLs. Company pages whose details and posts to sync. | [] |
| `linkedin_person_urls` | `array` | LinkedIn profile URLs. People whose profile and posts to sync. | [] |
| `trustpilot_domains` | `array` | Trustpilot company domains. Companies whose reviews to sync, by website domain. | [] |
| `google_place_ids` | `array` | Google Maps place IDs. Places whose reviews to sync. The places stream returns place_id values. | [] |
| `amazon_seller_ids` | `array` | Amazon seller IDs. Sellers whose profile, products and reviews to sync. | [] |
| `twitter_tweet_ids` | `array` | Tweet IDs. Tweets whose details, replies, quotes and retweets to sync: the number at the end of the tweet URL. | [] |
| `twitter_woeids` | `array` | Twitter trend locations. WOEIDs whose trending topics to sync, e.g. 1 for worldwide or 23424977 for the United States. | [] |
| `bluesky_post_urls` | `array` | Bluesky post URLs. Posts whose details, replies, quotes, likes and reposts to sync. | [] |
| `instagram_post_urls` | `array` | Instagram post URLs. Posts or reels whose details, comments and likes to sync. | [] |
| `instagram_hashtags` | `array` | Instagram hashtags. Hashtags whose posts to sync, without the #. | [] |
| `facebook_post_ids` | `array` | Facebook post IDs. Posts whose comments to sync: the post_id from the Facebook post streams. | [] |
| `linkedin_post_urls` | `array` | LinkedIn post URLs. Posts whose details to sync. | [] |
| `linkedin_job_urls` | `array` | LinkedIn job URLs. Job listings whose details to sync. | [] |
| `tiktok_video_urls` | `array` | TikTok video URLs. Videos whose details to sync. | [] |
| `amazon_asins` | `array` | Amazon ASINs. Products whose details to sync. | [] |
| `amazon_best_seller_categories` | `array` | Amazon best-seller categories. Category slugs whose best sellers to sync, e.g. software or electronics. | [] |
| `trustpilot_category_ids` | `array` | Trustpilot category IDs. Categories whose details and companies to sync. The Trustpilot categories stream returns category_id values. | [] |
| `trustpilot_user_ids` | `array` | Trustpilot user IDs. Reviewers whose reviews to sync. Review records carry the reviewer&#39;s user_id. | [] |
| `ai_prompts` | `array` | Google AI Mode prompts. Prompts to ask Google AI Mode, one record per prompt. | [] |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| twitter_posts | url.query | NoPagination | ✅ |  ✅  |
| twitter_users | url.query | NoPagination | ✅ |  ❌  |
| reddit_posts | url.query | DefaultPaginator | ✅ |  ✅  |
| reddit_comments | url.author.date.query | NoPagination | ✅ |  ✅  |
| reddit_users | url.query | NoPagination | ✅ |  ❌  |
| youtube_videos | url.query | NoPagination | ✅ |  ✅  |
| youtube_channels | url.query | NoPagination | ✅ |  ❌  |
| instagram_posts | url.query | NoPagination | ✅ |  ✅  |
| instagram_users | url.query | NoPagination | ✅ |  ❌  |
| tiktok_videos | url.query | NoPagination | ✅ |  ✅  |
| tiktok_users | url.query | NoPagination | ✅ |  ❌  |
| facebook_posts | url.query | NoPagination | ✅ |  ✅  |
| facebook_pages | url.query | NoPagination | ✅ |  ❌  |
| facebook_videos | video_id.query | NoPagination | ✅ |  ❌  |
| facebook_events | url.query | NoPagination | ✅ |  ❌  |
| threads_posts | url.query | NoPagination | ✅ |  ✅  |
| threads_users | url.query | NoPagination | ✅ |  ❌  |
| bluesky_posts | url.query | NoPagination | ✅ |  ✅  |
| bluesky_users | url.query | NoPagination | ✅ |  ❌  |
| linkedin_posts | url.query | DefaultPaginator | ✅ |  ✅  |
| linkedin_companies | url.query | DefaultPaginator | ✅ |  ❌  |
| linkedin_jobs | url.query | DefaultPaginator | ✅ |  ✅  |
| news_articles | url.query | NoPagination | ✅ |  ✅  |
| web_results | url.query | NoPagination | ✅ |  ❌  |
| forum_posts | url.query | DefaultPaginator | ✅ |  ❌  |
| google_places | place_id.query | NoPagination | ✅ |  ❌  |
| amazon_products | asin.query | DefaultPaginator | ✅ |  ❌  |
| trustpilot_companies | url.query | DefaultPaginator | ✅ |  ❌  |
| twitter_user_profiles | username.account | NoPagination | ✅ |  ❌  |
| twitter_user_tweets | url.account | NoPagination | ✅ |  ✅  |
| twitter_user_replies | url.account | NoPagination | ✅ |  ✅  |
| instagram_user_profiles | username.account | NoPagination | ✅ |  ❌  |
| instagram_user_posts | url.account | NoPagination | ✅ |  ✅  |
| tiktok_user_profiles | username.account | NoPagination | ✅ |  ❌  |
| threads_user_profiles | username.account | NoPagination | ✅ |  ❌  |
| threads_user_posts | url.account | NoPagination | ✅ |  ✅  |
| bluesky_user_profiles | username.account | NoPagination | ✅ |  ❌  |
| bluesky_user_posts | url.account | NoPagination | ✅ |  ✅  |
| truthsocial_user_posts | url.account | NoPagination | ✅ |  ✅  |
| youtube_channel_details | url.channel_url | NoPagination | ✅ |  ❌  |
| youtube_video_details | url.source_url | NoPagination | ✅ |  ❌  |
| youtube_video_comments | comment_id.source_url | NoPagination | ✅ |  ✅  |
| facebook_page_details | page_id.page_url | NoPagination | ✅ |  ❌  |
| facebook_page_posts | url.page_id | NoPagination | ✅ |  ✅  |
| facebook_page_reviews |  | NoPagination | ✅ |  ❌  |
| facebook_group_details | id.group_url | NoPagination | ✅ |  ❌  |
| facebook_group_posts | url.group_id | NoPagination | ✅ |  ✅  |
| linkedin_company_details | url.company_url | NoPagination | ✅ |  ❌  |
| linkedin_company_posts | url.company_url | DefaultPaginator | ✅ |  ✅  |
| linkedin_person_details | url.person_url | NoPagination | ✅ |  ❌  |
| linkedin_person_posts | url.person_url | DefaultPaginator | ✅ |  ✅  |
| trustpilot_company_reviews | review_id.company_domain | NoPagination | ✅ |  ✅  |
| google_place_reviews | review_id.place_id | NoPagination | ✅ |  ✅  |
| amazon_seller_profiles | seller_id.seller | NoPagination | ✅ |  ❌  |
| amazon_seller_reviews |  | DefaultPaginator | ✅ |  ❌  |
| facebook_locations | id.query | NoPagination | ✅ |  ❌  |
| trustpilot_categories | category_id.query | NoPagination | ✅ |  ❌  |
| twitter_user_followers | user_id.account | NoPagination | ✅ |  ❌  |
| twitter_user_following | user_id.account | NoPagination | ✅ |  ❌  |
| twitter_verified_followers | user_id.account | NoPagination | ✅ |  ❌  |
| instagram_user_followers | user_id.account | NoPagination | ✅ |  ❌  |
| instagram_user_following | user_id.account | NoPagination | ✅ |  ❌  |
| instagram_user_stories | url.account | NoPagination | ✅ |  ❌  |
| instagram_user_highlights | highlight_id.account | NoPagination | ✅ |  ❌  |
| instagram_highlight_stories | url.highlight_id | NoPagination | ✅ |  ❌  |
| bluesky_user_followers | user_id.account | NoPagination | ✅ |  ❌  |
| bluesky_user_following | user_id.account | NoPagination | ✅ |  ❌  |
| bluesky_user_likes | url.account | NoPagination | ✅ |  ❌  |
| twitter_tweet_details | url.tweet_id | NoPagination | ✅ |  ❌  |
| twitter_tweet_comments | url.tweet_id | NoPagination | ✅ |  ✅  |
| twitter_tweet_quotes | url.tweet_id | NoPagination | ✅ |  ✅  |
| twitter_tweet_retweets | user_id.tweet_id | NoPagination | ✅ |  ❌  |
| twitter_trends | name.woeid | NoPagination | ✅ |  ❌  |
| bluesky_post_details | url.post_url | NoPagination | ✅ |  ❌  |
| bluesky_post_comments | url.post_url | NoPagination | ✅ |  ✅  |
| bluesky_post_quotes | url.post_url | NoPagination | ✅ |  ✅  |
| bluesky_post_likes | user_id.post_url | NoPagination | ✅ |  ❌  |
| bluesky_post_reposts | user_id.post_url | NoPagination | ✅ |  ❌  |
| instagram_post_details | url.post_url | NoPagination | ✅ |  ❌  |
| instagram_post_comments | comment_id.post_url | NoPagination | ✅ |  ✅  |
| instagram_comment_replies | comment_id.parent_comment_id | NoPagination | ✅ |  ✅  |
| instagram_post_likes | user_id.post_url | NoPagination | ✅ |  ❌  |
| instagram_hashtag_posts | url.hashtag | NoPagination | ✅ |  ✅  |
| facebook_post_comments | comment_id.post_id | NoPagination | ✅ |  ✅  |
| facebook_page_photos | photo_id.page_id | NoPagination | ✅ |  ❌  |
| facebook_page_videos | video_id.delegate_page_id | NoPagination | ✅ |  ✅  |
| facebook_page_reels | video_id.reels_page_id | NoPagination | ✅ |  ✅  |
| facebook_group_search | url.query.group_id | NoPagination | ✅ |  ✅  |
| linkedin_post_details | url.post_url | NoPagination | ✅ |  ❌  |
| linkedin_job_details | url.job_url | NoPagination | ✅ |  ❌  |
| tiktok_video_details | video_id.tiktok_url | NoPagination | ✅ |  ❌  |
| google_place_details | place_id | NoPagination | ✅ |  ❌  |
| google_place_photos | photo_id.place_id | NoPagination | ✅ |  ❌  |
| amazon_product_details | asin | NoPagination | ✅ |  ❌  |
| amazon_seller_products | asin.seller | DefaultPaginator | ✅ |  ❌  |
| amazon_best_sellers | asin.category | DefaultPaginator | ✅ |  ❌  |
| trustpilot_category_details | category_id | NoPagination | ✅ |  ❌  |
| trustpilot_category_companies | business_unit_id.category_id | DefaultPaginator | ✅ |  ❌  |
| trustpilot_category_newest | business_unit_id.category_id | NoPagination | ✅ |  ❌  |
| trustpilot_user_reviews | review_id.user_id | DefaultPaginator | ✅ |  ✅  |
| google_ai_mode | prompt | NoPagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-05 | | Initial release by [@joshwallerr](https://github.com/joshwallerr) via Connector Builder |

</details>
