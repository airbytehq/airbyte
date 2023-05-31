# JDBC Destination

We are not planning to expose this destination in the UI yet. It serves as a base upon which we can build all of our other JDBC-compliant destinations.

The reasons we are not exposing this destination by itself are:
1. It is not terribly user-friendly (jdbc urls are hard for a human to parse)
1. Each JDBC-compliant db, we need to make sure the appropriate drivers are installed on the image. We don't want to frontload installing all possible drivers, and instead would like to be more methodical. Instead for each JDBC-compliant destination, we will extend this one and then install only the necessary JDBC drivers on that destination's image.
