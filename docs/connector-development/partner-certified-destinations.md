# Requirements for Airbyte Partners: “1.0” Bulk and Publish Destinations

## Welcome

**Thank you for contributing and committing to maintain your Airbyte destination connector 🥂**

This document outlines the minimum expectations for partner-certified destination.  We will **strongly** recommend that partners use the relevant CDK, but also want to support developers that *need* to develop in a different language.  This document covers concepts implicitly built into our CDKs for this use-case. 

## Definitions
**Partner Certified Destination:** A destination which is fully supported by the maintainers of the platform that is being loaded to. These connectors are not guaranteed by Airbyte directly, but instead the maintainers of the connector contribute fixes and improvements to ensure a quality experience for Airbyte users. Partner destinations are noted as such with a special “Partner” badge on the Integrations page, distinguishing them from other community maintained connectors on the Marketplace.


**Bulk Destinations:** A destination which accepts tables and columns as input, files, or otherwise unconstrained content. The majority of bulk destinations are database-like tabular (warehouses, data lakes, databases), but may also include file or blob destinations.  The defining characteristic of bulk destinations is that they accept data in the shape of the source (e.g. tables, columns or content doesn’t change much from the representation of the source).  These destinations can usually hold large amounts of data, and are the fastest to load. 

**Publish Destinations:** A publish-type destination, often called a “reverse ETL” destination loads data to an external service or API. These destinations may be “picky”, having specific schema requirements for incoming streams. Common publish-type use cases include: publishing data to a REST API, publishing data to a messaging endpoint (e.g email, push notifications, etc.), and publishing data to an LLM vector store. Specific examples include: Destination-Pinecone, Destination-Vectara, and Destination-Weaviate.  These destinations can usually hold finite amounts of data, and slower to load. 


