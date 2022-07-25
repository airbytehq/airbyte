# Getting Started
## Summary
This is a step-by-step guide for how to create an Airbyte source to read data from an HTTP API.
There are multiple ways to implement connectors for HTTP APIs depending on your needs and your toolset of choice.
In general, we recommend people build config-based connectors, and fallback to the Python CDK if more customization is needed.
The CDK is also available in C# .NET and in TypeScript/Javascript, but these implementations are not actively maintained by Airbyte.

### TODO: Here be a quick guide to help decide whether the dev should follow the low-code or python CDK tutorial...