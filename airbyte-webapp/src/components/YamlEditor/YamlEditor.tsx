import { CodeEditor } from "components/ui/CodeEditor";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { DownloadYamlButton } from "./DownloadYamlButton";
import styles from "./YamlEditor.module.scss";

export const YamlEditor: React.FC = () => {
  const { yamlManifest, setYamlManifest } = useConnectorBuilderState();

  return (
    <div className={styles.container}>
      <div className={styles.control}>
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
