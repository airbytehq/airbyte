# xkcd

## Overview

xkcd is a webcomic created in 2005 by American author Randall Munroe. The comic's tagline describes it as "a webcomic of romance, sarcasm, math, and language". Munroe states on the comic's website that the comic's name is not an initialism but "just a word with no phonetic pronunciation."

## Endpoints

xkcd API has only one endpoint that responds with the comic metadata.

## Quick Notes

- This is an open API, which means no credentials are necessary to access this data.
- This API doesn't accept query strings or POST params. The only way to iterate over the comics is through different paths, passing the comic number (https://xkcd.com/{comic_num}/json.html).

## API Reference

The API reference documents: https://xkcd.com/json.html
