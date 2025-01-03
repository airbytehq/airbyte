# Pardot Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 contains a number of fixes and updates to the Pardot source connector:

- Fixed authentication
- Migrate all existing streams to Pardot v5 API (except email_clicks which is only available in v4)
- Re-implement incremental syncs for existing streams where possible
- Add 23 new streams from the v5 API (folders, emails, engagement_studio_programs, folder_contents, forms, form_fields, form_handlers, form_handler_fields, landing_pages, layout_templates, lifecycle_stages, lifecycle_histories, list_emails, opportunities, tags, tracker_domains, visitor_page_views)
- Add additional configuration options to better handle large accounts (e.g. adjustable split-up windows, page size)
- Align to Pardot-recommended sort/filter/pagination conventions to avoid timeouts (based on Pardot support case #469072278)

The previous implementation of the authentication flow was no longer functional, preventing the instantiation of new sources. All users with existing connections should reconfigure the source and go through the authentication flow before attempting to sync with this connector. OSS users should be sure to manually update their source version to >=1.0.0 before attempting to configure this source.
