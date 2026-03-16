# LinkedIn Posts — OneLake Airbyte Destination Connector

Use these drafts for engagement and promotion. Attach the promotional image **`assets/onelake-airbyte-promo.png`** to your post to boost visibility. (If the image was generated in Cursor, it may be in your Cursor project folder under `assets/`; copy it into this repo’s `assets/` so it’s included when you push to GitHub.)

---

## Post 1: Short & punchy (with image)

**Copy:**

Ship data from any Airbyte source straight into Microsoft Fabric OneLake.

We built an Airbyte destination connector that writes to Lakehouse Files via the Blob API — with Service Principal or Managed Identity, so you can run it in Azure without storing secrets.

If you're stacking Fabric + Airbyte for analytics or ingestion, try it or contribute: [GitHub link]

#DataEngineering #MicrosoftFabric #OneLake #Airbyte #ETL #DataPipeline

---

## Post 2: Problem → solution (with image)

**Copy:**

Getting source data into Microsoft Fabric used to mean custom scripts or manual uploads.

We wanted a single pipeline: Airbyte for ingestion, OneLake for the lakehouse. So we built an Airbyte destination connector that:

✅ Writes directly to Fabric Lakehouse Files (OneLake)  
✅ Supports Service Principal and Managed Identity (no secrets on the box when running in Azure)  
✅ Lets you choose output path and format (CSV, JSONL)

Build the image, point Airbyte at your Fabric workspace and Lakehouse, and sync. Docs and repo in the comments.

#DataEngineering #MicrosoftFabric #OneLake #Airbyte #ELT

---

## Post 3: Technical / “how we did it” (optional image)

**Copy:**

How we connected Airbyte to Microsoft Fabric OneLake:

OneLake exposes an Azure Blob–compatible endpoint, so we extended the Airbyte CDK’s Azure Blob destination: fixed endpoint (onelake.blob.fabric.microsoft.com), workspace-as-container, and Lakehouse item as a path prefix (ItemName.Lakehouse/Files/...).

Auth: Service Principal (tenant + client id + secret) or Managed Identity so the connector can run in AKS/VM with no stored credentials.

We open-sourced the connector so others can run the same stack. Link in comments.

#DataEngineering #MicrosoftFabric #OneLake #Airbyte #OpenSource

---

## Image usage

- **Post 1 & 2:** Use the promotional image (Airbyte + OneLake / Fabric) as the main post image.
- **Post 3:** Image optional; a simple architecture diagram (Source → Airbyte → OneLake) can work.
- Add your **GitHub repo link** in the first comment so it’s easy to find.
