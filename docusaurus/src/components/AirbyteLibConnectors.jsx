export default function AirbyteLibConnectors({
    connectorsJSON,
  }) {
    const connectors = JSON.parse(connectorsJSON);
    return <ul>
    {connectors.map((connector) => <li key={connector.name_oss}>
        <a href={`${getRelativeDocumentationUrl(connector.spec_oss.documentationUrl)}#usage-with-airbyte-lib`}>{connector.name_oss}</a>
    </li>)}
    </ul>
}

function getRelativeDocumentationUrl(url) {
    const urlObj = new URL(url);
    return urlObj.pathname;
}