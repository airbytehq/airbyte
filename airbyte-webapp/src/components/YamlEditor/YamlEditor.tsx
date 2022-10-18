import { useState } from "react";
import { useDebounce, useLocalStorage } from "react-use";

import { CodeEditor } from "components/ui/CodeEditor";

import { ConfigMenu } from "./ConfigMenu";
import { DownloadYamlButton } from "./DownloadYamlButton";
import styles from "./YamlEditor.module.scss";
import { template } from "./YamlTemplate";

export const YamlEditor: React.FC = () => {
  const [locallyStoredEditorValue, setLocallyStoredEditorValue] = useLocalStorage<string>(
    "connectorBuilderEditorContent",
    template
  );
  const [editorValue, setEditorValue] = useState(locallyStoredEditorValue ?? "");
  useDebounce(() => setLocallyStoredEditorValue(editorValue), 500, [editorValue]);

  const handleEditorChange = (value: string | undefined) => {
    setEditorValue(value ?? "");
  };

  return (
    <div className={styles.container}>
      <div className={styles.control}>
        <DownloadYamlButton className={styles.downloadButton} yaml={editorValue} />
        <ConfigMenu className={styles.configMenuButton} />
      </div>
      <div className={styles.editorContainer}>
        <CodeEditor
          value={editorValue}
          language="yaml"
          theme="airbyte"
          onChange={handleEditorChange}
          lineNumberCharacterWidth={6}
        />
      </div>
    </div>
  );
};
