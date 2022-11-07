import Editor, { Monaco } from "@monaco-editor/react";
import React from "react";

import styles from "./CodeEditor.module.scss";

interface CodeEditorProps {
  value: string;
  language?: string;
  theme?: "airbyte-dark" | "airbyte-light" | "vs-dark" | "light";
  readOnly?: boolean;
  onChange?: (value: string | undefined) => void;
  height?: string;
  lineNumberCharacterWidth?: number;
}

// Converts 3-character hex values into 6-character ones.
// Required for custom monaco theme, because it fails when receiving 3-character hex values.
function expandHexValue(input: string) {
  const match = /^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$/.exec(input);
  if (match) {
    return `#${match[1].repeat(2)}${match[2].repeat(2)}${match[3].repeat(2)}`;
  }
  return input;
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
    monaco.editor.defineTheme("airbyte-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "string", foreground: expandHexValue(styles.tokenString) },
        { token: "type", foreground: expandHexValue(styles.tokenType) },
        { token: "number", foreground: expandHexValue(styles.tokenNumber) },
        { token: "delimiter", foreground: expandHexValue(styles.tokenDelimiter) },
        { token: "keyword", foreground: expandHexValue(styles.tokenKeyword) },
      ],
      colors: {
        "editor.background": "#00000000", // transparent, so that parent background is shown instead
      },
    });

    monaco.editor.defineTheme("airbyte-light", {
      base: "vs",
      inherit: true,
      rules: [
        { token: "string.yaml", foreground: expandHexValue(styles.lightString) },
        { token: "type", foreground: expandHexValue(styles.lightType) },
        { token: "number", foreground: expandHexValue(styles.lightNumber) },
        { token: "delimiter", foreground: expandHexValue(styles.lightDelimiter) },
        { token: "keyword", foreground: expandHexValue(styles.lightKeyword) },
      ],
      colors: {
        "editor.background": "#00000000", // transparent, so that parent background is shown instead
        "editorLineNumber.foreground": expandHexValue(styles.lightLineNumber),
        "editorLineNumber.activeForeground": expandHexValue(styles.lightLineNumberActive),
      },
    });
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
