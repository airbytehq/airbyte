import { ServiceDropdownOption } from "views/Connector/ServiceForm/components/Controls/ConnectorServiceTypeControl/utils";

export const sortRevealSources = (tech: string[] = [], sources: ServiceDropdownOption[]) => {
  const sourcesIndex: Record<string, string> = {
    "fa9f58c6-2d03-4237-aaa4-07d75e0c1396": "amplitude",
    "90916976-a132-4ce9-8bce-82a03dd58788": "bamboohr",
    "59c5501b-9f95-411e-9269-7143c939adbd": "bigcommerce",
    "47f25999-dd5e-4636-8c39-e7cea2453331": "bing_ads",
    "63cea06f-1c75-458d-88fe-ad48c7cb27fd": "braintree",
    "e7778cfc-e97c-4458-9ecb-b4f2bba8946c": "facebook_advertiser",
    "ec4b9503-13cb-48ab-a4ab-6ade4be46567": "freshdesk",
    "ef69ef6e-aa7f-4af1-a01d-ef775033524e": "github",
    "5e6175e5-68e1-4c17-bff9-56103bbb0d80": "gitlab",
    "253487c0-2246-43ba-a21f-5116b20a2c50": "google_adwords",
    "eff3616a-f9c3-11eb-9a03-0242ac130003": "google_analytics",
    "eb4c9e00-db83-4d63-a386-39cfa91012a8": "google_tag_manager",
    "36c891d9-4bd9-43ac-bad2-10e12756272c": "hubspot",
    "6acf6b55-4f1e-4fca-944e-1a3caef8aba8": "instagram",
    "d8313939-3782-41b0-be29-b3ca20d8dd3a": "intercom",
    "2e875208-0c0b-4ee4-9e92-1cb3156ea799": "iterable",
    "95e8cffd-b8c4-4039-968e-d32fb4a69bde": "klaviyo",
    "137ece28-5434-455c-8f34-69dc3782f451": "linked_in_advertiser",
    "00405b19-9768-4e0c-b1ae-9fc2ee2b2a8c": "looker",
    "b03a9f3e-22a5-11eb-adc1-0242ac120002": "mailchimp",
    "9e0556f4-69df-4522-a3fb-03264d36b348": "marketo",
    "eaf50f04-21dd-4620-913b-2a83f5635227": "microsoft_teams",
    "12928b32-bf0a-4f1e-964f-07e12e37153a": "mixpanel",
    "b2e713cd-cc36-4c0a-b5bd-b47cb8a0561e": "mongodb",
    "4f2f093d-ce44-4121-8118-9d13b7bfccd0": "netsuite",
    "1d4fdb25-64fc-4569-92da-fcdca79a8372": "okta",
    "b39a7370-74c3-45a6-ac3a-380d48520a83": "oracle_data_integrator",
    "5cb7e5fe-38c2-11ec-8d3d-0242ac130003": "pinterest",
    "d60a46d4-709f-4092-a6b7-2457f7d455f5": "presta_shop",
    "cd42861b-01fc-4658-a8ab-5d11d0510f01": "recurly",
    "69589781-7828-43c5-9f63-8925b1c1ccc2": "amazon_s3",
    "b117307c-14b6-41aa-9422-947e34922962": "salesforce",
    "fbb5fbe2-16ad-4cf4-af7d-ff9d9c316c87": "sendgrid",
    "cdaf146a-9b75-49fd-9dd2-9d64a0bb4781": "sentry",
    "9da77001-af33-4bcd-be46-6252bf9342b9": "shopify",
    "c2281cee-86f9-4a86-bb48-d23286b4c7bd": "slack",
    "374ebc65-6636-4ea0-925c-7d35999a8ffc": "smartsheet",
    "e2d65910-8c8b-40a1-ae7d-ee2416b2bfa2": "snowflake",
    "e094cb9a-26de-4645-8761-65c0c425d1de": "stripe",
    "badc5925-0485-42be-8caa-b34096cb71b5": "survey_monkey",
    "b9dc6155-672e-42ea-b10d-9f1f1fb95ab1": "twilio",
    "e7eff203-90bf-43e5-a240-19ea3056c474": "typeform",
    "40d24d0f-b8f9-4fe0-9e6c-b06c0f3f45e4": "zendesk",
    "79c1aa37-dae3-42ae-b333-d1c105477715": "zendesk",
    "325e0640-e7b3-4e24-b823-3361008f603f": "zendesk",
    "c8630570-086d-4a40-99ae-ea5b18673071": "zendesk",
    "3dc3037c-5ce8-4661-adc2-f7a9e3c5ece5": "zuora",
  };

  return sources.sort((x, y) => {
    const xIsIncludes = tech.includes(sourcesIndex[x.value]);
    const yIsIncludes = tech.includes(sourcesIndex[y.value]);
    return Number(yIsIncludes) - Number(xIsIncludes);
  });
};
