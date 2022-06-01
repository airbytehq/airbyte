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

import { ConnectionStateObject } from "core/request/AirbyteClient";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { useGetConnectionState } from "hooks/services/useConnectionHook";

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

const codeStyle = {
  fontFamily: '"Fira code", "Fira Mono", monospace',
  fontSize: 12,
  paddingLeft: "10px",
  marginBottom: "5px",
};

const StateBlock: React.FC<IProps> = ({ connectionId }) => {
  const [stateString, setStateString] = useState<string>(
    `// ${(<FormattedMessage id={`tables.State.stateLoading`} />)}`
  );
  const [loading, setLoading] = useState(false);
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { mutateAsync: getState } = useGetConnectionState();

  const loadState = async () => {
    setLoading(true);
    const state = await getState(connectionId);
    if (state?.state) {
      setStateString(formatState(state.state));
      setLoading(false);
    }
  };

  const saveState = useCallback(
    () => async () => {
      setLoading(true);
      setLoading(false);
    },
    []
  );

  const onSaveButtonClick = useCallback(() => {
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
        onValueChange={(code) => setStateString(code)}
        highlight={(code) => highlight(code, languages.js)}
        padding={10}
        contentEditable={!loading}
        style={codeStyle}
      />
      <LoadingButton type="submit" onClick={onSaveButtonClick} isLoading={loading} data-id="open-state-modal">
        <FormattedMessage id={`tables.State.save`} />
      </LoadingButton>
    </StateBlockComponent>
  );
};

const formatState = (state: ConnectionStateObject) => JSON.stringify(state, null, 2);

export default StateBlock;
