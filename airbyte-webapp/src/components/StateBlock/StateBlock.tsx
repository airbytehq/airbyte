import { highlight, languages } from "prismjs/components/prism-core";
import React, { useState, useEffect, useCallback } from "react";
import { FormattedMessage } from "react-intl";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";
import "prismjs/themes/prism.css";
import Editor from "react-simple-code-editor";
import styled from "styled-components";

import { H5, LoadingButton } from "components";
import ContentCard from "components/ContentCard";

import { ConnectionState, ConnectionStateObject } from "core/request/AirbyteClient";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { useGetConnectionState, useSetConnectionState } from "hooks/services/useConnectionHook";

type IProps = {
  connectionId: string;
};

const StateBlockComponent = styled(ContentCard)`
  margin-top: 12px;
  padding: 19px 20px 20px;
  // display: flex;
  align-items: top;
  justify-content: space-between;
`;

const Text = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor40};
  white-space: pre-line;
`;

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

type Validation = {
  valid: boolean;
  message?: string;
};

const StateBlock: React.FC<IProps> = ({ connectionId }) => {
  const [stateString, setStateString] = useState<string>(`// ...`);
  const [loading, setLoading] = useState(false);
  const [validation, setValidation] = useState<Validation>({ valid: true });
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { mutateAsync: getState } = useGetConnectionState();
  const { mutateAsync: setState } = useSetConnectionState();

  const loadState = async () => {
    setLoading(true);
    const state = await getState(connectionId);
    if (state?.state) {
      setStateString(formatState(state.state));
      setLoading(false);
    }
  };

  const saveState = async () => {
    setLoading(true);
    const stateObject = JSON.parse(stateString) as ConnectionState;
    const newState = await setState({ connectionId, state: stateObject });
    if (newState?.state) {
      setStateString(formatState(newState.state));
      setLoading(false);
    }
  };

  const onSaveButtonClick = useCallback(() => {
    const validationResponse = validateState(stateString);
    setValidation(validationResponse);
    if (!validationResponse.valid) return;

    openConfirmationModal({
      text: `tables.State.confirmModalText`,
      title: `tables.State.confirmModalTitle`,
      submitButtonText: "form.save",
      onSubmit: async () => {
        await saveState();
        closeConfirmationModal();
      },
      submitButtonDataId: "state",
    });
  }, [closeConfirmationModal, saveState, openConfirmationModal]);

  const loadStateMemoized = useCallback(() => {
    loadState();
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    loadStateMemoized();
  }, [loadStateMemoized]);

  return (
    <StateBlockComponent>
      <Text>
        <H5 bold>
          <FormattedMessage id={`tables.State.title`} />
        </H5>
        <FormattedMessage id={`tables.State.p1`} />. <FormattedMessage id={`tables.State.p2`} />.
      </Text>
      <Editor
        value={stateString}
        onValueChange={(code) => {
          if (!validation.valid) setValidation({ valid: true });
          setStateString(code);
        }}
        highlight={(code) => highlight(code, languages.js)}
        padding={10}
        disabled={loading}
        style={codeStyle}
      />
      {validation.valid === false && <ErrorText>{validation.message}</ErrorText>}
      <div style={{ paddingLeft: 19 }}>
        <LoadingButton
          type="submit"
          onClick={onSaveButtonClick}
          isLoading={loading}
          data-id="open-state-modal"
          disabled={!validation?.valid}
        >
          <FormattedMessage id={`tables.State.save`} />
        </LoadingButton>
      </div>
    </StateBlockComponent>
  );
};

const formatState = (state: ConnectionStateObject) => JSON.stringify(state, null, 4);

/**
 * There isn't much in the way of validation we can do other than:
 * 1. (TODO) ensuring that the original properties are still present
 * 2. (TODO) ensuring that there are no additional properties
 * 3. Checking that we have valid JSON
 */
const validateState: (state: string) => Validation = (state) => {
  let valid = true;
  let message: string | undefined;

  try {
    JSON.parse(state);
  } catch (e) {
    valid = false;
    message = "Invalid json";
  }

  return { valid, message: `Error: ${message}` };
};

export default StateBlock;
