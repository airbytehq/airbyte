import Editor from "@monaco-editor/react";

export const BuilderPage: React.FC = () => {
  const code = `version: "0.1.0"

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

  return (
    <Editor
      value={code}
      language="yaml"
      height="100%"
      theme="vs-dark"
      onChange={(val) => console.log(val)}
      options={{
        lineNumbersMinChars: 2,
        matchBrackets: "always",
        minimap: {
          enabled: false,
        },
      }}
    />
  );
};
