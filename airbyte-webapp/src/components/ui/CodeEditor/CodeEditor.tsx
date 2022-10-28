import Editor, { Monaco } from "@monaco-editor/react";
import React from "react";

import styles from "./CodeEditor.module.scss";

interface CodeEditorProps {
  value: string;
  language?: string;
  theme?: "airbyte" | "vs-dark" | "light";
  readOnly?: boolean;
  onChange?: (value: string | undefined) => void;
  height?: string;
  lineNumberCharacterWidth?: number;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  language,
  theme,
  readOnly,
  onChange,
  height,
  lineNumberCharacterWidth,
}) => {
  const setAirbyteTheme = (monaco: Monaco) => {
    monaco.editor.defineTheme("airbyte", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "string", foreground: styles.tokenString },
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
    <Editor
      beforeMount={setAirbyteTheme}
      value={value}
      onChange={onChange}
      language={language}
      theme={theme}
      height={height}
      options={{
        lineNumbersMinChars: lineNumberCharacterWidth ?? 2,
        readOnly: readOnly ?? false,
        matchBrackets: "always",
        minimap: {
          enabled: false,
        },
      }}
    />
  );
};
