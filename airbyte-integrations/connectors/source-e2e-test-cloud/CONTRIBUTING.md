# source-e2e-test-cloud: Contributor notes

## Cloud variant

This connector is the cloud variant of `source-e2e-test`.

It only allows `CONTINUOUS FEED` mode. The legacy `INFINITE FEED` and `EXCEPTION AFTER N` modes are excluded from cloud because the catalog is not customized for those modes and the connector should not emit infinite records in cloud.

If you change `CONTINUOUS FEED` mode, update and publish this cloud variant as well.
