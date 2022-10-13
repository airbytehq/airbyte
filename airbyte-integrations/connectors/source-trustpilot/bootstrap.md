[Trustpilot](https://www.trustpilot.com/) is a popular review website.

Trsutpilot API requires special token for its work, but all reviews can be consumed directly from website HTMLs easily.

This connector provides access to all reviews for specified company or app via parsing HTMLs.
It supports `full-refresh` and `incremental` synchronization strategies based on reversed-time order of retrieved reviews.
As `primary_key` it uses each review's `@id`, as `stream_cursor_field` it uses each review's `datePublished`.