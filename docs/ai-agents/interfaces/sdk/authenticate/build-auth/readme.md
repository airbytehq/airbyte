# Build your authentication flow

You must implement some kind of authentication flow so your customers can bring their data into Airbyte. However, you have many possible ways to achieve this. This section prescribes two possible methods.

- [**Authentication module**](authentication-module): The easiest way to implement authentication is to use the Authentication module (formerly known as Airbyte Embedded), an out-of-the-box widget you implement into your service. This method requires the least effort and uses Airbyte's own OAuth app and scopes.

- [**Build your own**](build-your-own): If you have discerning needs about your user experience, branding, or want to use your own OAuth app, you can build your own flow yourself. This method requires more effort, but allows for a more customized result.
