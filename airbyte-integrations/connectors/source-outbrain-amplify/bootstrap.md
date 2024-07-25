The (Outbrain Amplify Source is [a REST based API](https://www.outbrain.com//).
Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

## Outbrain-Amplify api stream

Outbrain Amplify is a content discovery and advertising platform that helps businesses and publishers promote their content to a wider audience. Customers can use Outbrain Amplify to promote their content across a range of premium publishers, including some of the biggest names in media. They can create custom campaigns, set specific targeting criteria, and monitor the performance of their campaigns in real-time. The platform also offers a range of tools and features to help customers optimize their campaigns and improve their ROI.
Offers a powerful way for businesses and publishers to reach new audiences and drive more traffic to their content. With its advanced targeting capabilities and robust reporting tools, the platform can help customers achieve their marketing goals and grow their businesses.

## Endpoints

- marketers stream --> Non-Non-Incremental
- campaigns by marketers stream. --> Non-Non-Incremental
- campaigns geo location stream. --> Non-Incremental
- promoted links for campaigns stream. --> Non-Incremental
- promoted links sequence for campaigns stream. --> Non-Incremental
- budgets for marketers stream. --> Non-Incremental
- performance report campaigns by marketers stream. --> Non-Incremental
- performance report periodic by marketers stream. --> Non-Incremental
- performance report periodic by marketers campaign stream. --> Non-Incremental
- performance report periodic content by promoted links campaign stream. --> Non-Incremental
- performance report marketers by publisher stream. --> Non-Incremental
- performance report publishers by campaigns stream. --> Non-Incremental
- performance report marketers by platforms stream. --> Non-Incremental
- performance report marketers campaigns by platforms stream. --> Non-Incremental
- performance report marketers by geo performance stream. --> Non-Incremental
- performance report marketers campaigns by geo stream. --> Non-Incremental
- performance report marketers by Interest stream. --> Non-Incremental
