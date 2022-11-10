import { CodeEditor } from "components/ui/CodeEditor";

import { useManifestTemplate } from "services/connectorBuilder/ConnectorBuilderApiService";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { DownloadYamlButton } from "./DownloadYamlButton";
import styles from "./YamlEditor.module.scss";

export const YamlEditor: React.FC = () => {
  const { yamlManifest, setYamlManifest } = useConnectorBuilderState();

  const template = useManifestTemplate();

  // const config = useConfig();
  // const url = `${config.connectorBuilderApiUrl}v1/manifest_template`;

  // const handleClick = async () => {
  //   console.log("url", url);
  //   const response = await fetch(url, {
  //     method: "get",
  //   });

  //   const responseJson = await response.json();

  //   alert(JSON.stringify(responseJson));
  // };

  return (
    <div className={styles.container}>
      <div className={styles.control}>
        {/* <Button onClick={handleClick}>Test Call to Server</Button> */}
        {`Template: ${template}`}
        <DownloadYamlButton yaml={yamlManifest} />
      </div>
      <div className={styles.editorContainer}>
        <CodeEditor
          value={yamlManifest}
          language="yaml"
          theme="airbyte"
          onChange={(value: string | undefined) => setYamlManifest(value ?? "")}
          lineNumberCharacterWidth={6}
        />
      </div>
    </div>
  );
};
