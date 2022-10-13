This is the first python custom source connector which is made for Timely.<br>
To get started using this connector, you will be needing three things.<br>

  1. Account ID
  2. Bearer Token
  3. Start-date

**Account ID** - Anyone who has admin access to Timelyapp.com you can find your account id, on the URL of your home page.

Once, you have the account create an application on the Timelyapp.com where you need to specify your application name, this will generate Client_secret, Client_id, and redirect_uri.

**Bearer Token** - To connect to the timelyapp API, I recommend using Postman or any other open source application that will get you the bearer token.
For Postman users, it will ask you to enter Auth url, Token url, Client_id, Client secret. For more details on how to work with timelyapp, please click [here](https://dev.timelyapp.com/#introduction)

**Start-date** - Please enter the start date in yy-mm--dd format to get the enteries from the start-date, this will pull all the record from the date entered to the present date.

That's all you need to get this connector working

**Working locally**- navigate yourself to the source-timely/sample_files/config.json, and enter the ID, token and date to get this connector working.
