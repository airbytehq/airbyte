import Editor from "@monaco-editor/react";
import React from "react";

interface CodeEditorProps {
  height?: string;
  code: string;
  language?: string;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({ code, height, language }) => {
  return (
    <Editor
      height={height ?? "200px"}
      language={language}
      value={code}
      options={{
        lineNumbersMinChars: 2,
        readOnly: true,
        matchBrackets: "always",
        minimap: {
          enabled: false,
        },
      }}
    />
  );
};
