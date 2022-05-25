import { isCloudApp } from "utils/app";

export const DEV_IMAGE_TAG = "dev";

export const getExcludedConnectorIds = (workspaceId: string) =>
  isCloudApp()
    ? [
        "200330b2-ea62-4d11-ac6d-cfe3e3f8ab2b", // Snapchat
        "2470e835-feaf-4db6-96f3-70fd645acc77", // Salesforce Singer
        ...(workspaceId !== "54135667-ce73-4820-a93c-29fe1510d348" // Shopify workspace for review
          ? ["9da77001-af33-4bcd-be46-6252bf9342b9"] // Shopify
          : []),
      ]
    : [];
