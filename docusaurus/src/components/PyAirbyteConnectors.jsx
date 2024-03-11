export default function PyAirbyteConnectors({
    connectorsJSON,
  }) {
    const connectors = JSON.parse(connectorsJSON);
    return <ul>
    {connectors.map((connector) => <li key={connector.name_oss}>
        <a href={`${getRelativeDocumentationUrl(connector)}#reference`}>{connector.name_oss}</a>
    </li>)}
    </ul>
}

function getRelativeDocumentationUrl(connector) {
    // get the relative path from the the dockerRepository_oss (e.g airbyte/source-amazon-sqs -> /integrations/sources/amazon-sqs)

    const fullDockerImage = connector.dockerRepository_oss;
    console.log(fullDockerImage);
    const dockerImage = fullDockerImage.split("airbyte/")[1];

    const [integrationType, ...integrationName] = dockerImage.split("-");

    return `/integrations/${integrationType}s/${integrationName.join("-")}`;
}
