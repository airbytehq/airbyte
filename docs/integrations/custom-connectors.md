# Custom Connectors

If you want to use connectors that are not part of the official Airbyte distribution, you can add them directly though the UI.

## Adding your connectors in the UI

There are only 3 easy steps to do that:

1.Get the `Docker` coordinate of a custom connector from `Dockerhub` \(or any image repository that Airbyte can access\).

2.In the UI, go to the Admin section, and click on `[+ New connector]` on the top right

![](https://lh4.googleusercontent.com/8lW_KRkw8w8q96JUJ7Snxj9MRC8toOyd7avLEj9anID53Q7Vj1bkPRSp8skV1VcIJPWsjWugX0pj0jCZ2jdaBwqhZED9E7DN5SRX_FWyRMdQu1eRojCTGm3xW2R8xYC9JE_kQtwn)

3.We will ask you for the display name, the Docker repository name, tag and documentation URL for that connector.

![](https://lh6.googleusercontent.com/UfEol2AKAR-7pKtJnzPNRoEDgOlEfoi9cA3SzB1NboENOZnniaJFfUGcCcVxYtzC8R97tnLwOh28Er5wS_aNujfXCSKUh0K7lhu7xUFYm4oiVCDlFdsdJNvgVihWp0u13ZNyzFuA)

Once this is filled, you will see your connector in the UI and your team will be able to use it, **from the UI and Airbyte's API too.**

Note that this new connector could just be an updated version of an existing connector that you adapted to your specific edge case. Anything is possible!

