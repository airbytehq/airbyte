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

// Converts 3-character hex values into 6-character ones.
// Required for custom monaco theme, because it fails when receiving 3-character hex values.
function expandHexValue(input: string) {
  // matches strings of the form #aaa
  const match = /^#([0-9a-f])\1{2}$/.exec(input);
  if (match) {
    return input + match[1].repeat(3);
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
    monaco.editor.defineTheme("airbyte", {
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
