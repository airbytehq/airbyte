# Tutorial

Airbyte is an open source alternative to tools like Fivetran and Stitch. We help you sync data from databases, APIs, and files into data warehouses.

In this tutorial, we'll walk through spinning up a local instance of Airbyte and syncing data from one Postgres database to another.

First of all, make sure you have Docker and Docker Compose installed. Then run the following commands:

```text
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Once you see an Airbyte banner, the UI is ready to go at [http://localhost:8000/](http://localhost:8000/). You should see an onboarding page. Enter your email if you want updates about Airbyte and continue.

Now you will see a wizard that allows you choose the data you want to send through Airbyte. As of our alpha launch, we have one database source \(Postgres\), two API sources \(an exchange rate API and the Stripe API\), and a file source. We're currently building an integration framework that makes it easy to create sources and destinations, so you should expect many more soon. Please reach out to us if you need a specific integration or would like to help build one.

For now, we will start out with a Postgres source and destination. Before we configure anything in the UI, we need databases and data. Run the following commands in a new terminal window to start backgrounded source and destination databases:

```text
docker run --rm --name airbyte-source -e POSTGRES_PASSWORD=password -p 2000:5432 -d postgres
docker run --rm --name airbyte-destination -e POSTGRES_PASSWORD=password -p 3000:5432 -d postgres
```

Add a table to the source database:

```text
docker exec -it airbyte-source psql -U postgres -c "CREATE TABLE users(id SERIAL PRIMARY KEY, col1 VARCHAR(200));"
```

Run a loop which will add records to this table every few seconds:

```text
while true
do
    COL1=$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1)
	docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users(col1) VALUES('$COL1');"
	sleep 3
done
```

Return to the UI and configure a source Postgres database. Use the name `airbyte-source` for the name and `Postgres`as the type. Since Airbyte is running locally, we'll need to point to the Docker local host `host.docker.internal`. Fill in the configuration fields as follows:

```text
Host: host.docker.internal
Port: 2000
User: postgres
Password: password
DB Name: postgres
```

Click on `Set Up Source` and the wizard should move on to allow you to configure a destination. We currently support BigQuery, Postgres, and file output for debugging, but Redshift, Snowflake, and other destinations are coming soon. For now, configure the destination Postgres database:

```text
Host: host.docker.internal
Port: 3000
User: postgres
Password: password
DB Name: postgres
```

After adding the destination, you can choose what tables and columns you want to sync. For this demo we recommend leaving the defaults and selecting "Every 5 Minutes" as the frequency. Click `Set Up Connection` to finish setting up the sync.

You should now see a list of sources with the source you just added. Click on it to find more information about your connection. This is the page where you can update any settings about this source and how it syncs. 

There should be a `Completed` job under the history section. If you click on that run, it will show logs from that run. One of biggest problems we've seen in tools like Fivetran is the lack of visibility when debugging. In Airbyte, allowing full log access and the ability to debug and fix integration problems is one of our highest priorities. We'll be working hard to make these logs accessible and understandable. 

Now let's verify that this worked. Let's output the contents of the destination db:

```text
docker exec airbyte-destination psql -U postgres -c "SELECT (id, col1) FROM public.users ORDER BY ID DESC LIMIT 5;"
```

You should see the last few rows of the `users` table. You can issue a manual sync and run the above command once more to see more recent records.

What happens when there are schema changes?  Stop the loop that you left running to generate rows with `Ctrl+C` and run the following command:

```text
docker exec -it airbyte-source psql -U postgres -c "ALTER TABLE public.users ADD COLUMN col2 VARCHAR(200);"
```

Then generate a new record using the new schema:

```text
docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users(col1, col2) VALUES('col1value', 'col2value');"
```

Now, manually sync again. This sync will automatically detect that there was a schema change. It will update the destination database's schema before inserting the new record.

Run the following command to see the new record in the destination Postgres database:

```text
docker exec airbyte-destination psql -U postgres -c "SELECT (id, col1, col2) FROM public.users ORDER BY ID DESC LIMIT 5;"
```

And there you have it. You've taken data from one database and replicated it to another. All of the actual configuration for this replication only took place in the UI. That's it for the tutorial, but this is just the beginning of Airbyte. If you have any questions at all, please reach out to us on [Slack](https://slack.airbyte.io/). We’re still in alpha, so If you see any rough edges or want to request an integration you need, please create an issue on our [Github](https://github.com/airbytehq/airbyte) or leave a thumbs up on an existing issue. 

Thank you and we hope you enjoy using Airbyte.

