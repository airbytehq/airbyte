import { CodeEditor } from "components/ui/CodeEditor";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { DownloadYamlButton } from "./DownloadYamlButton";
import { TestBuilderServer } from "./TestBuilderServer";
import styles from "./YamlEditor.module.scss";

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

  const setEditorTheme = (monaco: Monaco) => {
    monaco.editor.defineTheme("airbyte", {
      base: "vs-dark",
      inherit: true,
      rules: [
        // add logic to convert these two six character
        { token: "string", foreground: "#ffffff" },
        { token: "type", foreground: styles.tokenType },
        { token: "number", foreground: styles.tokenNumber },
        { token: "delimiter", foreground: styles.tokenDelimiter },
        { token: "keyword", foreground: styles.tokenKeyword },
      ],
      colors: {
        "editor.background": "#00000000", // transparent, so that parent background is shown instead
      },
    });

    monaco.editor.setTheme("airbyte");
  };

  return (
    <div className={styles.container}>
      <div className={styles.control}>
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
