import { CodeEditor } from "components/ui/CodeEditor";

import { useConnectorBuilderState } from "services/connector-builder/ConnectorBuilderStateService";

import { DownloadYamlButton } from "./DownloadYamlButton";
import styles from "./YamlEditor.module.scss";

export const YamlEditor: React.FC = () => {
  const { yamlDefinition, setYamlDefinition } = useConnectorBuilderState();

  return (
    <div className={styles.container}>
      <div className={styles.control}>
        <DownloadYamlButton yaml={yamlDefinition} />
      </div>
      <div className={styles.editorContainer}>
        <CodeEditor
          value={yamlDefinition}
          language="yaml"
          theme="airbyte"
          onChange={(value: string | undefined) => setYamlDefinition(value ?? "")}
          lineNumberCharacterWidth={6}
        />
      </div>
    </div>
  );
};
