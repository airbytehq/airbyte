export default function AirbyteLibConnectors({
    connectorsJSON,
  }) {
    const connectors = JSON.parse(connectorsJSON);
    return <ul>
    {connectors.map((connector) => <li key={connector.name_oss}>
        <a href={`${connector.spec_oss.documentationUrl}`}>{connector.name_oss}</a>
    </li>)}
    </ul>
}