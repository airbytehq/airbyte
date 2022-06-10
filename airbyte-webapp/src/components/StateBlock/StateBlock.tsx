import React, { useState, useEffect, useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { H5, Card } from "components";
import CodeEditor from "components/CodeEditor/CodeEditor";

import { ConnectionStateObject } from "core/request/AirbyteClient";
import { useGetConnectionState } from "hooks/services/useConnectionHook";

import styles from "./StateBlock.module.scss";

interface StateBlockProps {
  connectionId: string;
}

const StateBlock: React.FC<StateBlockProps> = ({ connectionId }) => {
  const [stateString, setStateString] = useState<string>();
  const [loading, setLoading] = useState(false);
  const { mutateAsync: getState } = useGetConnectionState();

  const loadState = async () => {
    setLoading(true);
    const state = await getState(connectionId);
    if (state?.state) {
      setStateString(formatState(state.state));
      setLoading(false);
    }
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
        <FormattedMessage id={"tables.connectionState.p1"} />.<br />
      </div>
      <CodeEditor
        code={loading ? "// loading..." : stateString || "// no state for this connector"}
        language={loading ? "javascript" : stateString ? "json" : "javascript"}
        setCode={setStateString}
        loading={loading}
        useModal
        modalTitleKey="tables.connectionState.confirmModalTitle"
        modalTextKey="tables.connectionState.confirmModalText"
      />
    </Card>
  );
};

const formatState = (state: ConnectionStateObject) => JSON.stringify(state, null, 4);

export default StateBlock;
