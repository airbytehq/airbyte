# This dockerfile only exists to pull and re-export this image converted to the local arch of this machine
# It is then consumed by the Dockerfile in this direcotry as "fishtownanalytics/dbt:1.0.0-dev"
FROM fishtownanalytics/dbt:1.0.0