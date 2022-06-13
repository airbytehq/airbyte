import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { H5, Card, CodeEditor } from "components";

import { useGetConnectionState } from "hooks/services/useConnectionHook";

import styles from "./StateBlock.module.scss";

interface StateBlockProps {
  connectionId: string;
}

export const StateBlock: React.FC<StateBlockProps> = ({ connectionId }) => {
  const { formatMessage } = useIntl();
  const state = useGetConnectionState(connectionId);

  const stateString = useMemo(() => {
    return state?.state
      ? JSON.stringify(state.state, null, 2)
      : formatMessage({ id: "tables.connectionState.noConnectionState" });
  }, [formatMessage, state.state]);

  return (
    <Card className={styles.stateBlock}>
      <H5 bold>
        <FormattedMessage id={"tables.connectionState.title"} />
      </H5>
      <CodeEditor code={stateString} language={state?.state ? "json" : undefined} />
    </Card>
  );
};
