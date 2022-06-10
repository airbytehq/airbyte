import Editor from "@monaco-editor/react";
import React, { useState, ReactElement } from "react";

import { LoadingButton } from "components";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";

import styles from "./CodeEditor.module.scss";

interface AirbyteCodeEditorProps {
  height?: string;
  code: string;
  language?: string;
  setCode: (newCode: string) => void;
  loading?: boolean;
  saveButtonCTA?: ReactElement | string;
  onSave?: (newCode: string) => Promise<ValidatorFeedback>;
  validate?: (newCode: string) => ValidatorFeedback;
  useModal?: boolean;
  modalTextKey?: string;
  modalTitleKey?: string;
}

export interface ValidatorFeedback {
  valid: boolean;
  errorMessage?: string;
}

const CodeEditor: React.FC<AirbyteCodeEditorProps> = ({
  code,
  loading,
  height,
  language,
  setCode,
  onSave,
  validate,
  saveButtonCTA,
  useModal,
  modalTextKey,
  modalTitleKey,
}) => {
  const [validation, setValidation] = useState<ValidatorFeedback>({ valid: true });
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const onValueChange = (newCode: string | undefined) => {
    if (!newCode) {
      return;
    }

    if (!validation.valid) {
      setValidation({ valid: true });
    }
    setCode(newCode);
  };

  const onClick =
    onSave || validate
      ? async () => {
          let valid = true;
          if (validate) {
            const validationResponse = validate(code);
            setValidation(validationResponse);
            valid = validationResponse.valid;
          }
          if (onSave && valid) {
            if (useModal) {
              openConfirmationModal({
                text: modalTextKey ?? "",
                title: modalTitleKey ?? "",
                submitButtonText: "form.saveChanges",
                onSubmit: async () => {
                  const updateResponse = await onSave(code);
                  if (updateResponse) {
                    setValidation(updateResponse);
                  }
                  closeConfirmationModal();
                },
              });
            } else {
              const updateResponse = await onSave(code);
              if (updateResponse) {
                setValidation(updateResponse);
              }
            }
          }
        }
      : undefined;

  return (
    <>
      <div style={{ paddingTop: 10 }} />
      <Editor
        height={height ?? "200px"}
        language={language ?? "json"}
        value={code}
        onChange={onValueChange}
        options={{
          matchBrackets: "always",
          minimap: {
            enabled: false,
          },
        }}
      />
      {validation.valid === false && <div className={styles.errorText}>{validation.errorMessage || "Invalid"}</div>}
      {onClick && (
        <div style={{ paddingLeft: 19, paddingTop: 10 }}>
          <LoadingButton type="submit" onClick={onClick} isLoading={loading} disabled={!validation?.valid}>
            {saveButtonCTA || "Save"}
          </LoadingButton>
        </div>
      )}
    </>
  );
};

export default CodeEditor;
