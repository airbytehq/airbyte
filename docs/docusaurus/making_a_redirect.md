# So you want to make a redirect in docs?

![Anywhere but here](https://camo.githubusercontent.com/098cc23055cd8e4409de6f4c91b1fea522a1aefc7986bfda9cc2055c029a2d3b/68747470733a2f2f6661726d352e737461746963666c69636b722e636f6d2f343133312f353036343836333337355f663636613038303034335f622e6a7067)

## Plugin Client Redirects
A silly name, but a useful plugin that adds redirect functionality to docusuaurs
[Official documentation here](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-client-redirects)

You will need to edit [this docusaurus file](https://github.com/airbytehq/airbyte/blob/master/docusaurus/docusaurus.config.js#L22)

You will see a commented section the reads something like this 

```js
//                        {
//                         from: '/some-lame-path',
//                         to: '/a-much-cooler-uri',
//                        },
```

Copy this section, replace the values, and [test it locally](locally_testing_docusaurus.md) by going to the 
path you created a redirect for and checked to see that the address changes to your new one.

*Note:* Your path **needs* a leading slash `/` to work
