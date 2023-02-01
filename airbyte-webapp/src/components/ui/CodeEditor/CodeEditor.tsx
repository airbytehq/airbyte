import Editor, { Monaco } from "@monaco-editor/react";
import { editor } from "monaco-editor/esm/vs/editor/editor.api";
import React from "react";

import styles from "./CodeEditor.module.scss";
import { Spinner } from "../Spinner";

interface CodeEditorProps {
  value: string;
  language?: string;
  theme?: "airbyte-dark" | "airbyte-light" | "vs-dark" | "light";
  readOnly?: boolean;
  onChange?: (value: string | undefined) => void;
  height?: string;
  lineNumberCharacterWidth?: number;
  onMount?: (editor: editor.IStandaloneCodeEditor) => void;
}

// Converts 3-character hex values into 6-character ones.
// Required for custom monaco theme, because it fails when receiving 3-character hex values.
// Only needed for non-dev mode, as that is when hex values get minified to 3 characters.
function expandHexValue(input: string) {
  const match = /^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$/.exec(input);
  if (match) {
    return `#${match[1].repeat(2)}${match[2].repeat(2)}${match[3].repeat(2)}`;
  }
  return input;
}

function cssCustomPropToHex(cssCustomProperty: string) {
  const varName = cssCustomProperty.replace(/var\(|\)/g, "");
  const bodyStyles = window.getComputedStyle(document.body);
  return expandHexValue(bodyStyles.getPropertyValue(varName).trim());
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  language,
  theme,
  readOnly,
  onChange,
  height,
  lineNumberCharacterWidth,
  onMount,
}) => {
  const setAirbyteTheme = (monaco: Monaco) => {
    monaco.editor.defineTheme("airbyte-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [
        { token: "string", foreground: cssCustomPropToHex(styles.darkString) },
        { token: "string.yaml", foreground: cssCustomPropToHex(styles.darkString) },
        { token: "string.value.json", foreground: cssCustomPropToHex(styles.darkType) },
        { token: "string.key.json", foreground: cssCustomPropToHex(styles.darkType) },
        { token: "type", foreground: cssCustomPropToHex(styles.darkType) },
        { token: "number", foreground: cssCustomPropToHex(styles.darkNumber) },
        { token: "delimiter", foreground: cssCustomPropToHex(styles.darkDelimiter) },
        { token: "keyword", foreground: cssCustomPropToHex(styles.darkKeyword) },
      ],
      colors: {
        "editor.background": "#00000000", // transparent, so that parent background is shown instead
      },
    });

    monaco.editor.defineTheme("airbyte-light", {
      base: "vs",
      inherit: true,
      rules: [
        { token: "string", foreground: cssCustomPropToHex(styles.lightString) },
        { token: "string.yaml", foreground: cssCustomPropToHex(styles.lightString) },
        { token: "string.value.json", foreground: cssCustomPropToHex(styles.lightString) },
        { token: "string.key.json", foreground: cssCustomPropToHex(styles.lightType) },
        { token: "type", foreground: cssCustomPropToHex(styles.lightType) },
        { token: "number", foreground: cssCustomPropToHex(styles.lightNumber) },
        { token: "delimiter", foreground: cssCustomPropToHex(styles.lightDelimiter) },
        { token: "keyword", foreground: cssCustomPropToHex(styles.lightKeyword) },
      ],
      colors: {
        "editor.background": "#00000000", // transparent, so that parent background is shown instead
        "editorLineNumber.foreground": cssCustomPropToHex(styles.lightLineNumber),
        "editorLineNumber.activeForeground": cssCustomPropToHex(styles.lightLineNumberActive),
      },
    });
  };

  return (
    <Editor
      beforeMount={setAirbyteTheme}
      onMount={onMount}
      loading={<Spinner />}
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
