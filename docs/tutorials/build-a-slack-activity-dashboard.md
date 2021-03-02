---
description: Using Airbyte and Apache Superset
---

# Build a Slack Activity Dashboard

This article will show how to use [Airbyte](http://airbyte.io) and [Apache Superset](https://superset.apache.org/) - a powerful, easy-to-use data exploration platform - in order to build a Slack activity dashboard showing:

* Total number of members of a Slack workspace
* The evolution of the number of Slack workspace members
* Evolution of weekly messages
* Evolution of messages per channel
* Members per time zone

Before we get started, let’s take a high-level look at how we are going to achieve creating a Slack dashboard using Airbyte and Apache Superset.

1. We will use the Airbyte’s Slack connector to get the data off a Slack workspace \(we will be using Airbyte’s own Slack workspace for this tutorial\).
2. We will save the data onto a PostgreSQL database.
3. Finally, using Apache Superset, we will implement the various metrics we care about.

Got it? Now let’s get started.

## Replicating Data from Slack to Postgres with Airbyte

### Deploying Airbyte

There are several easy ways to deploy Airbyte, as listed [here](https://docs.airbyte.io/). For this tutorial, I will just use the [Docker Compose method](https://docs.airbyte.io/deploying-airbyte/on-your-workstation) from my workstation: 

```text
# In your workstation terminal
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

The above command will make the Airbyte app available on `localhost:8000`. Visit the URL on your favorite browser, and you should see Airbyte’s dashboard \(if this is your first time, you will be prompted to enter your email to get started\). 

If you haven’t set Docker up, follow the [instructions here](https://docs.docker.com/desktop/) to set it up on your machine. 

### Setting Up Airbyte’s Slack Source Connector

Airbyte’s Slack connector will give us access to the data. So, we are going to kick things off by setting this connector to be our data source in Airbyte’s web app. I am assuming you already have Airbyte and Docker set up on your local machine. We will be using Docker to create our PostgreSQL database container later on.  
  
Now, let’s proceed. If you already went through the onboarding, click on the “new source” button at the top right of the Sources section. If you're going through the onboarding, then follow the instructions. 

You will be requested to enter a name for the source you are about to create. You can call it “slack-source”. Then, in the Source Type combo box, look for “Slack,” and then select it. Airbyte will then present the configuration fields needed for the Slack connector. So you should be seeing something like this on the Airbyte App:

![](https://lh3.googleusercontent.com/Gzs1SKXhWoPfO_M6ACRd_2Sy7Cgwrtn62QzX9PA_W3dh3SQQXMXpW9W6IVIkIPJz_VrcZm6EY_rMUVBrw0mZAx-Lkr5n1yC9NfC6U3Z09iAwnHN-kfg_epzlmBJQmsdh4nJT_aDg)

The first thing you will notice is that this connector requires a Slack token. So, we have to obtain one. If you are not a workspace admin, you will need to ask for permission.

Let’s walk through how we would get the Slack token we need.

Assuming you are a workspace admin, open the Slack workspace and navigate to \[Workspace Name\] &gt; Administration &gt; Customize \[Workspace Name\]. In our case, it will be Airbyte &gt; Administration &gt; Customize Airbyte \(as shown below\):

![](https://lh4.googleusercontent.com/4j0AL88vstGgOXDbRYDlKdibjsaOi_e961MhlUlbq-zASK51-gPuZ1EqqY9M7xRg6cOV7Uc6O5TvAv4W-DBku4gLe883FGAsb7Tmiib9iuVCyM4HSFtya8y9-8ieJOxGXi9c-IDX)

In the new page that opens up in your browser, you will then need to navigate to **Configure apps**.![](https://lh6.googleusercontent.com/lrDV-_KaHaQa0GVcoK85XR-MgAFEGct80x5gDQwPMDSTOkqAJseHFJrKrHn_MLEXkfW0DB6CU3SahlaHsPwjljOpyDFE5DxLS5PM0L1F3J1UO_ry3VDzqegTpYAtHAX5KYMmCN4q)

In the new window that opens up, click on **Build** in the top right corner.

![](https://lh3.googleusercontent.com/Prnmrug8bw8OZnK5qeu3x8EqyynCAyPKUtceAVppBrT4k4nRMlQsTpTiFX4pgNjZMnWBofTtnyv6yz0L2Was02kH487h5ldTT9UxejwlS8EWnCgEwLYW2vSLGya6hDVNULSfeRKe)

Click on the **Create an App** button.

![](https://lh3.googleusercontent.com/MrRDw81ewhSXDDuaS0x_RyIUp7wxBv2JtfIDaDtNz6GxDgmqbtZSGtNXMuWrxXY6h0f6KULtp7qdV1bpAqZPTlESwj-Dm9_FpEYgwEwcqKoVbNrueWFCobAxajG-3aK_QMphjLNo)

In the modal form that follows, give your app a name - you can name it `airbyte_superset`, then select your workspace from the Development Slack Workspace.

![](https://lh4.googleusercontent.com/W3AG5Ux2eXxnYQvbdXQJrGZ5aoitmEoWpsUnWRj1I121AvrC3e_FKl95CQSf3f9BA-w-fRBK6oWQW6I-kqsk1tqSOtHUP0gmaG2UHtIYnj1Nw9Opubw3ZbMoZoOD1EyCN2CweM0j)

Next, click on the **Create App** button. You will then be presented with a screen where we are going to set permissions for our `airbyte_superset` app, by clicking on the **Permissions** button on this page.

![](https://lh5.googleusercontent.com/t_2TvwmPMEH5qxKpQDOxe5w9h_splA_umCvtkquLCJEeFsMjQHECkzp4ITvH3vh6M7eMKKqGhNFSAJpbbeQ0iQjXwG5jhBRYRzg2EZgKU6VlaMymm8TB5i8-gaZtjBp7V_AhMdaD)

In the next screen, navigate to the scope section. Then, click on the **Add an OAuth Scope** button. This will allow you to add permission scopes for your app. At a minimum, your app should have the following permission scopes:

![](https://lh3.googleusercontent.com/vTZlEqUETw5fyZk6-hFp7hvIqc51qXVlk4lIaBnu1U8iottkGQkxAJRmXMb40eaT0IdnCbNG-WKdAPpZhkZmyiJH6OPVaXI80CXOrkg7U07zFXbO3FaY3uX-SVEwIEdTnZXdMNBZ)

Then, we are going to add our created app to the workspace by clicking the **Install to Workspace** button.

![](https://lh5.googleusercontent.com/G0WgwnYHNZ672pmjGLjbsAyuj7J9I8D98W091zVAhEkLf5xoItpfjEzZOdFA3cf1qJWClZmZQs_0JyET2lEcdJnas87pxWLbKlJM3wSbGwhaBXkJArnm8MJy2ks-1-hLN13xSiql)

Slack will prompt you that your app is requesting permission to access your workspace of choice. Click Allow.

![](https://lh3.googleusercontent.com/GiwkTAZbFguXY0rcRIJQ1zWCd6JDAmMRWDn8wwQoBROvI_1d2wxbc9HJyWOVeiQOVdJPa2oc9XDM0GwfC73gswBmna19L7MzF3bC4GWSwVh9yZQGBFUOLYiS3Q6ldtM6wg_BKhrU)

After the app has been successfully installed, you will be navigated to Slack’s dashboard, where you will see the Bot User OAuth Access Token. 

This is the token you will provide back on the Airbyte page, where we dropped off to obtain this token. So make sure to copy it and keep it in a safe place.

Now that we are done with obtaining a Slack token, let’s go back to the Airbyte page we dropped off and add the token in there. 

We will also need to provide Airbyte with `start_date`. This is the date from which we want Airbyte to start replicating data from the Slack API, and we define that in the format: `YYYY-MM-DDT00:00:00Z`.

We will specify ours as `2020-09-01T00:00:00Z`. We will also tell Airbyte to exclude archived channels and not include private channels, and also to join public channels, so the latter part of the form should look like this:  


![](https://lh4.googleusercontent.com/LzpJh-a49HW7DOMDbUevzTNuVQ8dkLO2QproWnWYb7c8_ncPUA6-cRZkC_5PemwZ2Qbuaa1PK9TqpLS0IPTXNExPQNJQw9a0GHprk_RwhF6xQFS989xOJLVpt3RpYDskL5nQUaWq)

Finally, click on the **Set up source** button for Airbyte to set the Slack source up.

If the source was set up correctly, you will be taken to the destination section of Airbyte’s dashboard, where you will tell Airbyte where to store the replicated data. 

### Setting Up Airbyte’s Postgres Destination Connector

For our use case, we will be using PostgreSQL as the destination.

Click the **add destination** button in the top right corner, then click on **add a new destination**.

![](https://lh3.googleusercontent.com/wAXNJ8bvSGWlxrmA0o709TDIqEzTai8pZYRE_kOABr6J-f_V1MqjqCmFezSccXgPcnKAHeegjLbpPbyVcjD5vIjtCD9lm9Mb53ScC3_NW6eBH8Fjq6KwzxX8N8XdBGWC2whA3Jg_)

In the next screen, Airbyte will validate the source, and then present you with a form to give your destination a name. We’ll call this destination slack-destination. Then, we will select the Postgres destination type. Your screen should look like this now:

![](https://lh3.googleusercontent.com/b5Z-mrJazm2E6d9WuGbPuy5Ce0gaEvGFrSPZPTzc9peyxfvY8XlWVO8Yg1nizA3YOeI7tpd76K4s-N5ba3X4jjtnPOh1ROpLm4N1Ouj6PmlOvxJhnxQyUu-yE9GkRqUg67CgVn6f)

Great! We have a form to enter Postgres connection credentials, but we haven’t set up a Postgres database. Let’s do that!

Since we already have Docker installed, we can spin off a Postgres container with the following command in our terminal:

```text
docker run --rm --name slack-db -e POSTGRES_PASSWORD=password -p 2000:5432 -d postgres
```

\(Note that the Docker compose file for Superset ships with a Postgres database, as you can see [here](https://github.com/apache/superset/blob/master/docker-compose.yml#L40)\). 

The above command will do the following:

* create a Postgres container with the name slack-db,
* set the password to password,
* expose the container’s port 5432, as our machine’s port 2000. 
* create a database and a user, both called postgres. 

With this, we can go back to the Airbyte screen and supply the information needed. Your form should look like this:

![](https://lh5.googleusercontent.com/NIa_3YtECKjnpxwFPtP-mUC0GQk_Nw8ccyGyxJglSF5qHBYX2Pm1xhaZlm39LII0FEHjQGR0028na12FOUEQBsdVjv5yoXLS4-1OItYLLbOj1npVZKxm6IdaAXH6Fo4SLmY8Km5i)

Then click on the **Set up destination** button. 

### Setting Up the Replication

You should now see the following screen:

![](https://lh5.googleusercontent.com/2d-xT10BeLgDIR7nVAZpbbP54u1cSpyo2QN-znJWdhKSCJhuvU4wndl-hgJj2_HVkS0sSvgdfLLQ4MMloqToMWYqiZmJhuIRwvnvyUADDPuEQtE8LalWVKb6Kuod3FwbYhIevVJ8)

Airbyte will then fetch the schema for the data coming from the Slack API for your workspace. You should leave all boxes checked and then choose the sync frequency - this is the interval in which Airbyte will sync the data coming from your workspace. Let’s set the sync interval to every 24 hours.

Then click on the **Set up connection** button. 

Airbyte will now take you to the destination dashboard, where you will see the destination you just set up. Click on it to see more details about this destination.

![](https://lh6.googleusercontent.com/4klteF8sCyAxVcsZPJGJkMUpxqBGSCJg0G2L3zcy3AQn4ubVKZGwRYodjKv5anc1DIGP2DDvfrTOqUX4GCSn4gLuk0CSNVP4vmtVRH_Zq6i1VzRB8sATl3O2T4UwJ5FewJ0aXHCL)

You will see Airbyte running the very first sync. Depending on the size of the data Airbyte is replicating, it might take a while before syncing is complete.

![](https://lh3.googleusercontent.com/FMf73mdFM9tetz-kGniyO3iaxSR26st48nMVQHRH7RlQNxDSfh-lVthMaKag5f44IqJaI2Dv1fBkIVGHOIR2YWWj63lP-qxZS7F1XvZd5MpKNIy6wI001Z1Q7oL0lEnnIUwQgVRk)

When it’s done, you will see the **Running status** change to **Succeeded**, and the size of the data Airbyte replicated as well as the number of records being stored on the Postgres database.

![](https://lh3.googleusercontent.com/iORV_GS8hLjVInUL0qf3mXaeJRqYi5uVgS83wzSYfGVBv5_7l1MInuSd66EOPzLXcrow1YVAKoqc9F7zyOmyJ48FcooGiwqA4w3xjNRZjqKIydj5JXqlXvX5Cm9Rr5bZBAFcBgXy)

To test if the sync worked, run the following in your terminal:

```text

```

This should output the rows in the users’ table.

To get the count of the users’ table as well, you can also run:

```text
docker exec slack-db psql -U postgres -c "SELECT count(*) FROM public.users;"
```

Now that we have the data from the Slack workspace in our Postgres destination, we will head on to creating the Slack dashboard with Apache Superset.

## Setting Up Apache Superset for the Dashboards

### Installing Apache Superset

Apache Superset, or simply Superset, is a modern data exploration and visualization platform. To get started using it, we will be cloning the Superset repo. Navigate to a destination in your terminal where you want to clone the Superset repo to and run:

```text
git clone https://github.com/apache/superset.git
```

It’s recommended to check out the latest branch of Superset, so run:

```text
cd superset
```

And then run:

```text
git checkout latest
```

Superset needs you to install and build its frontend dependencies and assets. So, we will start by installing the frontend dependencies:

```text
npm install
```

Note: The above command assumes you have both Node and NPM installed on your machine.

Finally, for the frontend, we will build the assets by running:

```text
npm run build
```

After that, go back up one directory into the Superset directory by running:

```text
cd..
```

Then run:

```text
docker-compose up
```

This will download the Docker images Superset needs and build containers and start services Superset needs to run locally on your machine. 

Once that’s done, you should be able to access Superset on your browser by visiting [`http://localhost:8088`](http://localhost:8088), and you should be presented with the Superset login screen.

Enter username: **admin** and Password: **admin** to be taken to your Superset dashboard.

Great! You’ve got Superset set up. Now let’s tell Superset about our Postgres Database holding the Slack data from Airbyte.

### Setting Up a Postgres Database in Superset

To do this, on the top menu in your Superset dashboard, hover on the Data dropdown and click on **Databases**.

![](https://lh6.googleusercontent.com/cDJ4Y31jqEWk0qW7jtcdY6Kk2TW1RuLBxDkYqGCJx-9RJFrl0EzBVw8bnBsps9RTVREdnUdH__tt6Gq17R0P76MiP4gudgfyTh4ByMTJSIw4dobj9CBCvoKZxTfCsVIRQT0MsKoI)

In the page that opens up, click on the **+ Database** button in the top right corner.

![](https://lh6.googleusercontent.com/A3cMMfO5-x__Kje8mdTFb_4uOh9NxLhgzIPovpw-ONvz-iq_NG2kaMZSFH0eRjDgxoROLXh0eaQUpXgoTEVG1qatgmRGhTpKGELRZ16KJ7p_WPBp9T-XqYaaWHeuB7eK4prjp-9m)

Then, you will be presented with a modal to add your Database Name and the connection URI.

![](https://lh3.googleusercontent.com/bhG6P66E2O-0GkDclJz1DbPA3pG_8c5c-Hayw7ors98D8cr_YOhn52PRTNG02TmLdP1MrrbhvERrAWw6vO3_gQoSilPki2ryRoB-yZj8mXmr3ae8eM4-yDwfDJ8GrHyM6eXRoJUe)

Let’s call our Database `slack_db`, and then add the following URI as the connection URI:

```text
postgresql://postgres:password@docker.for.mac.localhost:2000/postgres
```

 If you are on a Windows Machine, yours will be:

```text
postgresql://postgres:password@docker.for.win.localhost:2000/postgres
```

Note: We are using `docker.for.[mac|win].localhost` in order to access the localhost of your machine, because using just localhost will point to the Docker container network and not your machine’s network.

Your Superset UI should look like this:

![](https://lh4.googleusercontent.com/D4f3RuKni0kA5R5D3C_cuy6rGYdcspkEGxBtvYd9972ILRTzXHOys64duMwA4LIYYBfDrbNPInlMqQJe_9xbOoxL3rSJ61ss_ZBUARgtHBURz7tezj7jCr7vDn59m9H9l5srx9Gg)

We will need to enable some settings on this connection. Click on the **SQL LAB SETTINGS** and check the following boxes:

![](https://lh5.googleusercontent.com/1LZSV7GibdaI7Me3ssJN_BKOe4hb7AHAxyGtUXFDznXOooKkuq3IWofcaCNk0O3N8v5baNAOhmTnn76-imfrQrXwAnPZPrxAB2KUbv_fqP2cAnp6hL9ngXxMKcCk0olVGAKd5uqI)

Afterwards, click on the **ADD** button, and you will see your database on the data page of Superset.

![](https://lh6.googleusercontent.com/zFI74IT_GnkkBtALc02WZA5HNwAyJP4e497WgjQ7uc1-gMHyIt3hXEpwWbxmckeFwCS0GIla8KjDJeYOI39U4RntSUkgIyGe1aat4RtIb34js2siLa6X1jBciKAC7Y5Tr7KpCGj-)

### Importing our dataset

Now that you’ve added the database, you will need to hover over the data menu again; now click on **Datasets**.

![](https://lh4.googleusercontent.com/8K5Aw4YC8C9W86yMTHioEAWUG5zg8UAmQ4o6CtIfDt3XQPcb-WF71TJMZKirH-sSL44p-iQ7rjnSN6N2R0UYAhSWv61u7ZjF73UXrZGGZn96UJUhRW-IBCjke4J_QHwe-Inxl6LW)

Then, you will be taken to the datasets page: 

![](https://lh6.googleusercontent.com/S_VjjllUUSwXh-bgKsdz18lXw4csT67qE5AQPdHlF7lsbRAQwZZTyON1UoYSys0zqzs_GBwLVt_C7fkEpqXP7hZxJsWO9ifMt_xDKxQNzvc0FZYwHYeXwYfB5ZN-usMXIUnvUAvF)

We want to only see the datasets that are in our `slack_db` database, so in the Database that is currently showing All, select `slack_db`  and you will see that we don’t have any datasets at the moment. 

![](https://lh5.googleusercontent.com/iR-3ARfEAMsxrarW_-IEFXNlGeANrZLkIVGBS45p0DXf87l3O8z5ceoDpAr8Z9VhkE7XASym3yYW76ZS-uJQF7EWIcTGc4XTIj-o5-ZFvvWhyJpdtND5ZRQWebnMSuXR8cDMMbo4)

![](https://lh4.googleusercontent.com/DRhj7rUclW1JRej-FBIgr6FoCqRpN75aJsF_-g-lvY5WAcuzvUYXWBXVnthcTuUUCrUSQWpoIl1CSv6WdOG9gboVxh7YyuZx_2UI86uM-zVIUREtZsrL45tMi-zefDwBzxmFCktd)

You can fix this by clicking on the **+ DATASET** button and adding the following datasets. 

Note: Make sure you select the public schema under the Schema dropdown.

![](https://lh5.googleusercontent.com/7H-XUoCkXToyTOgRkbBUOWQKcBCsn3ePkN0Vf2y2PGNj26YO5FmYeh7xE1iRfUFfoOV2D7RbvX693bCSnvTQ2dvw3Cjx1dPBN83oYN-dCrhCJvXLIVSKCtmFSmoq-4dnPjBCA_D6)

Now that we have set up Superset and given it our Slack data, let’s proceed to creating the visualizations we need. 

Still remember them? Here they are again:

* Total number of members of a Slack workspace
* The evolution of the number of Slack workspace members
* Evolution of weekly messages
* Evolution of weekly threads created
* Evolution of messages per channel
* Members per time zone

## Creating Our Dashboards with Superset

### Total number of members of a Slack workspace

To get this, we will first click on the users’ dataset of our `slack_db` on the Superset dashboard.

![](https://lh4.googleusercontent.com/KUbSlekcXSAL-VVMvd11WFdZIvcbmBGkmOFb2Whr50VRe0fiy_t-7GK6yjIy-8vJz04kPlg8VFH2ggaibC5iz-IT4Jgk5__3UFrUs8DC9FQIOI_VDqk89xKOk7cGuZ0NNfHkR-6N)

Next, change **untitled** at the top to **Number of Members**.

![](https://lh5.googleusercontent.com/z-QJ2sHTF8dtwwcCRzT_vcUFVIVwLEJ8Rm5njVH4QgRSJ_KL5EU-Qervxadr4iEp4i8VOtcKocW8MKXFXmBjSf4xbfWSIovKRPP9dCCrVzyT2BZbN3UDHE3la3N95cNtB1GYONyk)

Now change the **Visualization Type** to **Big Number,** remove the **Time Range** filter, and add a Subheader named “Slack Members.” So your UI should look like this:  
  
![](https://lh5.googleusercontent.com/DKFklY209XeCtTAMPGfMigfNu84GgyNSkJ1pRv-Nx4D7JJFeWFzCE6biNuBjhk6zCAjuNGT355GgFl9cslgBV44cFiO2m04ik-h1MxlnbUZKv9GFjBmkzww72lBQ7pVglk7wY_id)

Then, click on the **RUN QUERY** button, and you should now see the total number of members.  
  
Pretty cool, right? Now let’s save this chart by clicking on the **SAVE** button.

![](https://lh3.googleusercontent.com/M2UEAJcoulX1f_Eby2mokwp4fGIIV44n5SnOCO8ZYX1KWeudvbBT_4FiCHDAvEbFQ8iPWC9HLMMpXB2w1fyl3dsISl-fFMXXqmsK0DvoPCpItTsnPPC0SYhHNYhwARt8V99GsK4s)

Then, in the **ADD TO DASHBOARD** section, type in “Slack Dashboard”, click on the “Create Slack Dashboard” button, and then click the **Save** button.

Great! We have successfully created our first Chart, and we also created the Dashboard. Subsequently, we will be following this flow to add the other charts to the created Slack Dashboard.

### Casting the ts column

Before we proceed with the rest of the charts for our dashboard, if you inspect the **ts** column on either the **messages** table or the **threads** table, you will see it’s of the type `VARCHAR`. We can’t really use this for our charts, so we have to cast both the **messages** and **threads**’ **ts** column as `TIMESTAMP`. Then, we can create our charts from the results of those queries. Let’s do this.

First, navigate to the **Data**  menu, and click on the **Datasets** link. In the list of datasets, click the **Edit** button for the **messages** table.

![](https://lh6.googleusercontent.com/fht1PV2_UGc-c2Pt1QuB2YO1HDJOOQqpHQORMka4l0suRwdS-4ESwJfCHwVEjUkGYQfkd6S0cXYKnc9n94kHY09WBvKtvivnxbDVFJOTncRrObxb8rsOwdeVPKcot8JEGs7JsnYD)

You’re now in the Edit Dataset view. Click the **Lock** button to enable editing of the dataset. Then, navigate to the **Columns** tab, expand the **ts** dropdown, and then tick the **Is Temporal** box. 

![](https://lh6.googleusercontent.com/0ACAJ16aWHBdEDzBzym_G8UkjQl02weadbn0VyEG9HitnpaMTccRM0VHf-adMDGvUNfnmkVazzm6lU5ouZCpzbG9_68_4q_FQTi7BypGuPV4z_N8HmHC6jax3Qy0Utbb8c2ykwqL)

Persist the changes by clicking the Save button.

### The evolution of the number of Slack workspace members

In the exploration page, let’s first get the chart showing the evolution of the number of Slack members. To do this, make your settings on this page match the screenshot below:  


![](https://lh4.googleusercontent.com/Hk7sTWlry5oEkiUeAqzVa9smRshtbDiXFMUT6e-aKJn1iPKGitb4vUnaH4HzKdf-irpvuvj_PamRCN4zQQq6BBeUN-Tv9dXNdZ6x58ryG3eksNfst3CFGpIvn43PYqLy-_c-H8Mg)

Save this chart onto the Slack Dashboard.

### Evolution of weekly messages posted

Now, we will look at the evolution of weekly messages posted. Let’s configure the chart settings on the same page as the previous one.

![](https://lh6.googleusercontent.com/JrXIZZft5YzI9tvYeEMqpQ9fVLvyf_XokQGjH4K2jzwfu5BDoc-OEW6FiJT3_RU9l30VYtOzF0Hnl_VN8BB9M70oP8h6ovUOyBzWn2jzW3KT2_Oj-eKF2Q5mblFG_yvWgwn1XvGT)

Remember, your visualization will differ based on the data you have.

### Evolution of weekly threads created

Now, we are finished with creating the message chart. Let's go over to the thread chart. You will recall that we will need to cast the **ts** column as stated earlier. So, do that and get to the exploration page, and make it match the screenshot below to achieve the required visualization:

![](https://lh4.googleusercontent.com/PJc7ETdzHSBgYLM5RbPESCvFl6TZs5AFzyYQ6VHeaaowurMlr7zmyXUDOHYdyeWmeEkBF6Qa9BNfjuyUg_lHrNTyQOx7m4whysVNDCvDjGFKMX7JeFNPGrEra3CiZimZcSSnhKX-)

### Evolution of messages per channel

For this visualization, we will need a more complex SQL query. Here’s the query we used \(as you can see in the screenshot below\): 

```text
SELECT CAST(m.ts as TIMESTAMP), c.name, m.text
FROM public.messages m
INNER JOIN public.channels c
ON m.channel_id = c_id
```

![](https://lh3.googleusercontent.com/8me7-UFnCfn2ev77sunFIYWd3fsD8PAHe7wgrUMP_diWAzaKPZSMYHnsDPT6uJu1V0NYKhgdhTEZN6VgqWMkQoNVihlOC0ccTCV1kLh0HmnZqJIc1yUbKIFPx6Q_wZBDxSGpeoXk)

Next, click on **EXPLORE** to be taken to the exploration page; make it match the screenshot below:

![](https://lh4.googleusercontent.com/LrQBiYOWcsbLYlrHK8DD9k4Kx_BOmHq1cZhXM6qlH8erXvkVJpphj0m_E4-dcBN-nuHSOQP2hqgFNXBxRwzXoOGic0q9ulvBU-0RHI5ev3C7UqlipIc3BsMuoZvWjC_BKGjzJq0h)

Save this chart to the dashboard.

### Members per time zone

Finally, we will be visualizing members per time zone. To do this, instead of casting in the SQL lab as we’ve previously done, we will explore another method to achieve casting by using Superset’s Virtual calculated column feature. This feature allows us to write SQL queries that customize the appearance and behavior of a specific column.

For our use case, we will need the updated column of the users table to be a `TIMESTAMP`, in order to perform the visualization we need for Members per time zone. Let’s start on clicking the edit icon on the users table in Superset

![](https://lh6.googleusercontent.com/wyfO7w2_PEEsjTq54_dOeILxts3UhsUuaDwxjNWw6obKsrEidvhDNGIBbLaVjzrJTmSVDoxqonGYa2X2TCE1nJ8l1lmVIlUcSqBxeINfqZJEFk-NRRCYkuMAnHR2GelQxuTCtQJN)

You will be presented with a modal like so:

![](https://lh5.googleusercontent.com/D72fnbaxzpv-5hKCqrh4XqnCEWmngVeBDJrAT-PFCi6Gwfb1lrBwpljaIBo7QpHNNa_TyNkXVCA8PK9mmyVQ_9nNQPcL3J0JX2J-2QRO58eDFijpzYThIDTQ2McSqOwaeIi-87a_)

Click on the **CALCULATED COLUMNS** tab:

![](https://lh5.googleusercontent.com/RqC0FMNonza4OO9bL8PrmMUlpQbIRwr4dESvwtnwXvs4b4Tdh_dq2v36Nk7OvSGDdV4QH_NH3dt0ha9i15VM0b_8u8oZ97FUfgxFTX7iYY_9XKUbzwkXG60vaq5CMHGAnEYbnSxQ)

Then, click on the **+ ADD ITEM** button, and make your settings match the screenshot below. 

![](https://lh3.googleusercontent.com/CNqQys8AEgfrI4fAeA97LMbWbEE-xWE6RqDPeGX2BqjlSUtM2TaZLEhuyg55xJ_5jns7rwlCwfBu0MG_bdkxWucASojEz9LDlOH_zesOzXT7XWVpqxHAR4tGbYJY9x_OSBT2g02T)

Then, go to the **exploration** page and make it match the settings below:

![](https://lh4.googleusercontent.com/OJSt-iVLaHtMXCqy2JqVZZZIL4IRR5HRHrWYKuoZ55y6CfzCzaeL49UKFuci1t7kn09ZJ-bgeW7_GqtV2M794mLKH-aPTkBNjCRo_uBF-KwbcMCZ-mjCkcMa7JFm1IXKIMwE2lrs)

Now save this last chart, and head over to your Slack Dashboard. It should look like this:

![](https://lh5.googleusercontent.com/ryfvbvf0Wm6eMTFdtQMpiFNVEkZ4kNlLHaTylkp3Bz5kQMQnUTg6_JuApntnArcS-6gx80vW7FoREkkcgzxFk8KD733E-DLybFBXAv4bMLBfBjwlOu62Qou9md7olZ7gSWHqnMRc)

Of course, you can edit how the dashboard looks to fit what you want on it.

## Conclusion

In this article, we looked at using Airbyte’s Slack connector to get the data from a Slack workspace into a Postgres database, and then used Apache Superset to craft a dashboard of visualizations.If you have any questions about Airbyte, don’t hesitate to ask questions on our [Slack](https://slack.airbyte.io)! If you have questions about Superset, you can join the [Superset Community Slack](https://superset.apache.org/community/)!

