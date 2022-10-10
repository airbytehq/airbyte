import Editor, { Monaco } from "@monaco-editor/react";
import { useState } from "react";
import { useDebounce, useLocalStorage } from "react-use";

import { Button } from "components/ui/Button";

import styles from "./YamlEditor.module.scss";

export const YamlEditor: React.FC = () => {
  // TODO: replace with API call to get starting contents
  const template = `version: "0.1.0"

    definitions:
      schema_loader:
        type: JsonSchema
        file_path: "./source/schemas/{{ options['name'] }}.json"
      selector:
        type: RecordSelector
        extractor:
          type: DpathExtractor
          field_pointer: []
      requester:
        type: HttpRequester
        name: "{{ options['name'] }}"
        http_method: "GET"
        authenticator:
          type: BearerAuthenticator
          api_token: "{{ config['api_key'] }}"
      retriever:
        type: SimpleRetriever
        $options:
          url_base: TODO "your_api_base_url"
        name: "{{ options['name'] }}"
        primary_key: "{{ options['primary_key'] }}"
        record_selector:
          $ref: "*ref(definitions.selector)"
        paginator:
          type: NoPagination
    
    streams:
      - type: DeclarativeStream
        $options:
          name: "customers"
        primary_key: "id"
        schema_loader:
          $ref: "*ref(definitions.schema_loader)"
        retriever:
          $ref: "*ref(definitions.retriever)"
          requester:
            $ref: "*ref(definitions.requester)"
            path: TODO "your_endpoint_path"
    check:
      type: CheckStream
      stream_names: ["customers"]  
      `;

  const [editorValue, setEditorValue] = useState(template);
  const [, setStoredEditorContent] = useLocalStorage<string>("connectorBuilderEditorContent", template);

  useDebounce(() => setStoredEditorContent(editorValue), 500, [editorValue]);

  const handleEditorChange = (value: string | undefined) => {
    setEditorValue(value ?? "");
  };

  const setEditorTheme = (monaco: Monaco) => {
    monaco.editor.defineTheme("airbyte", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "type", foreground: "7f7eff" },
        { token: "string", foreground: "ffffff" },
        { token: "number", foreground: "fe866c" },
        { token: "delimiter", foreground: "f8d54e" },
        { token: "keyword", foreground: "00cbd6" },
      ],
      colors: {
        "editor.background": "#0d0d2d",
      },
    });

    monaco.editor.setTheme("airbyte");
  };

  return (
    <div className={styles.container}>
      <div className={styles.control}>
        <Button className={styles.exportButton}>Download YAML</Button>
      </div>
      <div className={styles.editorContainer}>
        <Editor
          beforeMount={setEditorTheme}
          value={editorValue}
          language="yaml"
          theme="airbyte"
          onChange={handleEditorChange}
          options={{
            lineNumbersMinChars: 6,
            matchBrackets: "always",
            minimap: {
              enabled: false,
            },
            padding: {
              top: 20,
              bottom: 20,
            },
          }}
        />
      </div>
    </div>
  );
};
