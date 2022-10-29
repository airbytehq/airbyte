# Restcountries.com

restcountries.com provides an API to get information about countries such as the country code,
population, country dial code etc...
More information can be found on the [website](https://restcountries.com/) and the associated public Gitlab [project](https://gitlab.com/amatos/rest-countries)

This source makes use of the version 2 endpoint.

## Perequisites

restcountries.com is an open API , no credentials are needed to setup the source.

## Supported sync modes

- Full Refresh

## Supported streams

Currently one stream, to get all the informations for all the countries available.

* countries

## Performance considerations

No performance limitation , however given the nature of the source and in order to limit the bandwith on this free API, refreshing the data once day or less should be more than enough.

## Changelog





