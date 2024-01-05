## What is a source connector?

A source connector is a software component or tool designed to streamline the extraction of data from a source system or application. Serving as a bridge between diverse data environments, it guarantees the seamless and accurate transfer of information from the source to the target system.

To perform data integration and transfer processes from Amazon Ads to an alternative destination system or data storage solution via Airbyte, the initial step involves configuring an Amazon Ads source connector. 

## Prerequisites

Ensure you have the following prepared for your setup process:

* Client ID
* Client Secret
* Refresh Token
* Region
* Access to your Amazon Ads account
* Start Date (Optional)
* Profile IDs (Optional)
* Marketplace IDs (Optional)

## Set up the Amazon Ads source connector in Airbyte

The tabs below provide comprehensive instructions for configuring the Amazon Ads source connector with both Airbyte Cloud and Airbyte Open Source.

<Tabs
  defaultValue="cloud"
  values={[
    {label: <center>Airbyte Cloud</center>, value: 'cloud'},
    {label: <center>Airbyte Open Source</center>, value: 'opensource'},
  ]}>
<TabItem value="cloud">

<ol>
<li>Log into your Airbyte Cloud account.</li>
<li>In the left navigation bar, click <b>Sources</b>. In the top-right corner, click <b>+ new source</b>.</li>
<li>On the Source setup page, select <b>Amazon Ads</b> from the Source type dropdown and provide a name for this connector.</li>
<li>Click <b>Authenticate your Amazon Ads account</b>.</li>
<li>Log in to your Amazon Ads account and authorize access to it.</li>
<li>Select <b>Region</b> to pull data from North America (NA), Europe (EU), or Far East (FE). See <a href="https://advertising.amazon.com/API/docs/en-us/reference/api-overview">docs </a> for more details.</li>
<li>For the <b>Start Date (Optional)</b>, specify the date in YYYY-MM-DD format for generating reports. It should not be more than 60 days in the past. If not specified, today's date is used. The date is treated in the timezone of the processed profile.</li>
<li>For the <b>Profile IDs (Optional) </b>, enter the profiles for which you want to fetch data. Refer to the documentation for more details.</li>
<li>For the <b>Marketplace IDs (Optional)</b>, specify the marketplace IDs for which you want to fetch data. <br />

<b>Note:</b> If Profile IDs are also selected, profiles will be included if they match either the Profile ID or the Marketplace ID. 
</li>
<li>Click <b>Set up source</b>.</li>
</ol>

</TabItem>
<TabItem value="opensource">

To utilize the <a href="https://advertising.amazon.com/API/docs/en-us">Amazon Ads API</a>, you must first initiate the <a href="https://advertising.amazon.com/API/docs/en-us/setting-up/overview">onboarding process </a>, which comprises several steps and may require several days for completion. 

Once all steps are successfully finalized, obtain essential credentials, including the Amazon client application Client ID, Client Secret, and Refresh Token.

Complete the steps below to set up a new source:
<ol>
<li>Log in to your Amazon Ads account and authorize access to it.</li>
<li>Select <b>Region</b> to pull data from North America (NA), Europe (EU), or Far East (FE). See <a href="https://advertising.amazon.com/API/docs/en-us/reference/api-overview">docs </a> for more details.</li>
<li>For the <b>Start Date (Optional)</b>, specify the date in YYYY-MM-DD format for generating reports. It should not be more than 60 days in the past. If not specified, today's date is used. The date is treated in the timezone of the processed profile.</li>
<li>For the <b>Profile IDs (Optional) </b>, enter the profiles for which you want to fetch data. Refer to the documentation for more details.</li>
<li>For the <b>Marketplace IDs (Optional)</b>, specify the marketplace IDs for which you want to fetch data. <br />

<b>Note:</b> If Profile IDs are also selected, profiles will be included if they match either the Profile ID or the Marketplace ID. 
</li>
<li>Click <b>Set up source</b>.</li>
</ol>

</TabItem>
</Tabs>

### Data type mapping

Below is the data type mapping to be used for your operation:

| Integration Type | Airbyte Type |
---------------------| -------------
`string` |`string`
`int`, `float`, `number` | `number`
`date` | `date`
`datetime` | `datetime`
`array` | `array`
`object` | `object`
## Supported sync modes

The Amazon Ads source connector supports the following sync modes:

* **Full Refresh:** In this sync mode, all data is retrieved from the source system during each synchronization, ensuring a complete and up-to-date dataset. It involves a comprehensive extraction of information, making it suitable for scenarios where the entire dataset needs to be refreshed regularly.
* **Incremental:** This sync mode captures only the changes made since the last synchronization, minimizing data transfer and improving efficiency. It is ideal for scenarios where you want to synchronize only the new or modified records, reducing the processing time and resource requirements.

## Supported streams

This source is capable of syncing the following streams:

<table class="feedback">
<tbody>
    <tr>
    <td>
        <ul>
        <li>Profiles </li>
        <li>Portfolios </li>
        <li>Sponsored Brands Campaigns</li>
        <li>Sponsored Brands Campaigns</li>
        <li>Sponsored Brands Ad groups</li>
        <li>Sponsored Brands Keywords</li>
        <li>Sponsored Display Campaigns</li>
        <li>Sponsored Display Ad groups</li>
        <li>Sponsored Display Product Ads</li>
        <li>Sponsored Display Targetings</li>
        <li>Sponsored Display Creatives</li>
        <li>Sponsored Display Budget Rules</li>
        <li>Sponsored Products Campaigns</li>
        <li>Sponsored Display Ad groups</li>
        <li>Sponsored Display Product Ads</li>
        <li>Sponsored Display Targetings</li>
        </ul>
    </td>
        <td>
        <ul>
        <li>Sponsored Display Creatives</li>
        <li>Sponsored Display Budget Rules</li>
        <li>Sponsored Products Campaigns</li>
        <li>Sponsored Products Ad groups</li>
        <li>Sponsored Products Ad Group Bid Recommendations</li>
        <li>Sponsored Products Ad Group Suggested Keywords</li>
        <li>Sponsored Products Keywords</li>
        <li>Sponsored Products Negative keywords</li>
        <li>Sponsored Products Campaign Negative keywords</li>
        <li>Sponsored Products Ads</li>
        <li>Sponsored Products Targetings</li>
        <li>Brands Reports</li>
        <li>Brand Video Reports</li>
        <li>Display Reports (Contextual targeting only)</li>
        <li>Products Reports</li>
        <li>Attribution Reports</li>
        </ul>
    </td>
    </tr>
</tbody>
</table>

:::info Important highlights

- All reports are generated based on the timezone of the target profile
- Campaign reports may occasionally lack data or may not present records. This situation can arise when there are no clicks or views associated with the campaigns on the requested day.
- Report data synchronization only covers the last 60 days.


:::

## Next steps

To sync data to your desired destination connectors, see the sections below.

<div class="container" style={{ padding: 0 }}>
  <div class="row is-multiline">
    <div class="col col--6">
      <Link class="card" to="https://docs.airbyte.com/category/destinations" style={{ height: '100%' }}>
        <div class="card__contents">
          <div>
            <img src="../../../../img/screenshots/docv-sdk-rn.svg" alt="react native" class="sdkImageRN"></img><span class="imageSpan"><span class="headerText"><b>Destinations</b></span>
            </span>
          </div>
            <div>
              <p>Learn how to set up different destination connectors for your data syc. </p>
            </div>
        </div>
      </Link>
    </div>
    <div class="col col--6">
      <Link class="card" to="https://docs.airbyte.com/using-airbyte/getting-started/" style={{ height: '100%' }}>
        <div class="card__contents">
          <div>
            <span class="imageSpan">
              <img src="../../../../img/screenshots/docv-sdk-rn.svg" alt="react native" class="sdkImageRN"></img><span class="headerText"><b>Using Airbyte</b></span>
            </span>
          </div>
            <div>
              <p>Learn how to use Airbyte for critical data operations.</p>
            </div>
        </div>
      </Link>
    </div>
        <div class="col col--6">
      <Link class="card" to="https://docs.airbyte.com/category/deploy-airbyte" style={{ height: '100%' }}>
        <div class="card__contents">
          <div>
            <span class="imageSpan">
              <img src="../../../../img/screenshots/docv-sdk-rn.svg" alt="react native" class="sdkImageRN"></img><span class="headerText"><b>Managing Airbyte</b></span>
            </span>
          </div>
            <div>
              <p>Learn how to effectively manage multiple users, and multiple teams using Airbyte all in one place. </p>
            </div>
        </div>
      </Link>
    </div>
  </div>
</div>

