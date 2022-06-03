import { highlight, languages } from "prismjs/components/prism-core";
import React, { useState, ReactElement } from "react";
import Editor from "react-simple-code-editor";
import styled from "styled-components";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";
import "prismjs/themes/prism.css";

import { LoadingButton } from "components";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";

const ErrorText = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.redColor};
  white-space: pre-line;
`;

const codeStyle = {
  fontFamily: '"Fira code", "Fira Mono", monospace',
  fontSize: 12,
  marginTop: "5px",
  marginLeft: "10px",
  marginBottom: "5px",
};

interface AirbyteCodeEditorProps {
  code: string;
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

  const onValueChange = (newCode: string) => {
    if (!validation.valid) setValidation({ valid: true });
    setCode(newCode);
  };

  const onClick = async () => {
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
          submitButtonText: "form.saveChange",
          onSubmit: async () => {
            const updateResponse = await onSave(code);
            if (updateResponse) setValidation(updateResponse);
            closeConfirmationModal();
          },
        });
      } else {
        const updateResponse = await onSave(code);
        if (updateResponse) setValidation(updateResponse);
      }
    }
  };

  return (
    <>
      <Editor
        value={code}
        onValueChange={onValueChange}
        highlight={(code) => highlight(code, languages.js)}
        padding={10}
        disabled={loading}
        style={codeStyle}
      />
      {validation.valid === false && <ErrorText>{validation.errorMessage || "Invalid"}</ErrorText>}
      <div style={{ paddingLeft: 19 }}>
        <LoadingButton type="submit" onClick={onClick} isLoading={loading} disabled={!validation?.valid}>
          {saveButtonCTA || "Save"}
        </LoadingButton>
      </div>
    </>
  );
};

export default CodeEditor;
