# Hubspot Migration Guide

## Upgrading to 2.0.0

Note: this change is only breaking if you are using PropertyHistory stream

With this update, we have access to historical property changes for Deals and Companies, just like we have it for Contacts. That is why Property History stream was renamed to Contacts Property History and two new streams were added: Deals Property History and Companies Property History.
This is a breaking change because Property History by fact was replaced with Contacts Property History, so you need to refresh your schema (reset data as an option) then make Contacts Property History selected and run a sync job.
