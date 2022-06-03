import React, { useState, useEffect, useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { H5, Card } from "components";
import CodeEditor, { ValidatorFeedback } from "components/CodeEditor/CodeEditor";

import { ConnectionState, ConnectionStateObject } from "core/request/AirbyteClient";
import { useGetConnectionState, useUpdateConnectionState } from "hooks/services/useConnectionHook";

import styles from "./StateBlock.module.scss";

interface StateBlockProps {
  connectionId: string;
}

const StateBlock: React.FC<StateBlockProps> = ({ connectionId }) => {
  const [stateString, setStateString] = useState<string>(`// ...`);
  const [loading, setLoading] = useState(false);
  const { mutateAsync: getState } = useGetConnectionState();
  const { mutateAsync: updateState } = useUpdateConnectionState();

  const loadState = async () => {
    setLoading(true);
    const state = await getState(connectionId);
    if (state?.state) {
      setStateString(formatState(state.state));
      setLoading(false);
    }
  };

  const saveState: () => Promise<ValidatorFeedback> = async () => {
    setLoading(true);
    const stateObject = JSON.parse(stateString) as ConnectionState;
    const response = await updateState({ connectionId, state: stateObject });
    setLoading(false);
    if (response.state) setStateString(formatState(response.state));
    return { valid: response.successful, errorMessage: response.errorMessage };
  };

  const loadStateMemoized = useCallback(() => {
    loadState();
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    loadStateMemoized();
  }, [loadStateMemoized]);

  return (
    <Card className={styles.stateBlock}>
      <div className={styles.descriptionText}>
        <H5 bold>
          <FormattedMessage id={"tables.connectionState.title"} />
        </H5>
        <FormattedMessage id={"tables.connectionState.p1"} />. <FormattedMessage id={"tables.connectionState.p2"} />.
      </div>
      <CodeEditor
        code={stateString}
        setCode={setStateString}
        onSave={saveState}
        validate={validateState}
        loading={loading}
        saveButtonCTA={<FormattedMessage id={"tables.connectionState.save"} />}
        useModal
        modalTitleKey="tables.connectionState.confirmModalTitle"
        modalTextKey="tables.connectionState.confirmModalText"
      />
    </Card>
  );
};

const formatState = (state: ConnectionStateObject) => JSON.stringify(state, null, 4);

/**
 * There isn't much in the way of validation we can do other than:
 * 1. (TODO) ensuring that the original properties are still present
 * 2. (TODO) ensuring that there are no additional properties
 * 3. Checking that we have valid JSON
 */
const validateState: (state: string) => ValidatorFeedback = (state) => {
  let valid = true;
  let message: string | undefined;

  try {
    JSON.parse(state);
  } catch (e) {
    valid = false;
    message = "Invalid json";
  }

  return { valid, errorMessage: `Error: ${message}` };
};

export default StateBlock;
