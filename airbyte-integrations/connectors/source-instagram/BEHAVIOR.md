# source-instagram: Unique Behaviors

## 1. Hidden Per-Record API Calls for Carousel Media Children

When syncing media records that have children (carousel posts), the `InstagramMediaChildrenTransformation` makes an additional API call for EACH child media ID during record transformation. A carousel post with 10 slides triggers 10 separate HTTP requests to the `/media` endpoint to fetch detailed information (media_type, media_url, timestamp, etc.) for each child.

**Why this matters:** What appears to be a simple media stream read can silently multiply into many additional API calls proportional to the number of carousel slides across all media records. This directly impacts sync duration and rate limit consumption, and the additional calls are invisible from the manifest configuration.
