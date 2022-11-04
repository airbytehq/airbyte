import { useMonaco } from "@monaco-editor/react";
import { load, YAMLException } from "js-yaml";
import { editor } from "monaco-editor/esm/vs/editor/editor.api";
import { useEffect, useRef, useState } from "react";
import { useDebounce, useLocalStorage } from "react-use";

import { CodeEditor } from "components/ui/CodeEditor";

import { StreamsListRequestBodyManifest } from "core/request/ConnectorBuilderClient";

import { DownloadYamlButton } from "./DownloadYamlButton";
import styles from "./YamlEditor.module.scss";
import { template } from "./YamlTemplate";

interface YamlEditorProps {
  localStorageKey: string;
  setJsonValue: (value: Record<string, object>) => void;
}

export const YamlEditor: React.FC<YamlEditorProps> = ({ localStorageKey, setJsonValue }) => {
  const yamlEditorRef = useRef<editor.IStandaloneCodeEditor>();

  const [locallyStoredYaml, setLocallyStoredYaml] = useLocalStorage<string>(localStorageKey, template);
  const [yamlValue, setYamlValue] = useState(locallyStoredYaml ?? template);
  useDebounce(() => setLocallyStoredYaml(yamlValue), 500, [yamlValue]);

  const monaco = useMonaco();

  useEffect(() => {
    if (monaco && yamlEditorRef.current && yamlValue) {
      const errOwner = "yaml";
      console.log(yamlValue);
      const yamlEditorModel = yamlEditorRef.current.getModel();

      try {
        const json = load(yamlValue) as StreamsListRequestBodyManifest;
        setJsonValue(json);

        // clear editor errors
        if (yamlEditorModel) {
          monaco.editor.setModelMarkers(yamlEditorModel, errOwner, []);
        }
      } catch (err) {
        console.log(err.message);
        if (err instanceof YAMLException) {
          const mark = err.mark;
          if (yamlEditorModel) {
            monaco.editor.setModelMarkers(yamlEditorModel, errOwner, [
              {
                startLineNumber: mark.line + 1,
                startColumn: mark.column + 1,
                endLineNumber: mark.line + 1,
                endColumn: mark.column + 2,
                message: err.message,
                severity: monaco.MarkerSeverity.Error,
              },
            ]);
          }
        }
      }
    }
  }, [yamlValue, monaco, setJsonValue]);

  return (
    <div className={styles.container}>
      <div className={styles.control}>
        <DownloadYamlButton yaml={yamlValue} />
      </div>
      <div className={styles.editorContainer}>
        <CodeEditor
          value={yamlValue}
          language="yaml"
          theme="airbyte"
          onChange={(value) => setYamlValue(value ?? "")}
          lineNumberCharacterWidth={6}
          onMount={(editor) => (yamlEditorRef.current = editor)}
        />
      </div>
    </div>
  );
};
