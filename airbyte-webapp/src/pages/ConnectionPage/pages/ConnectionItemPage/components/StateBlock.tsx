import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { H5, Card } from "components";

import { useGetConnectionState } from "hooks/services/useConnectionHook";

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
    <Card $withPadding>
      <H5 bold>
        <FormattedMessage id="tables.connectionState.title" />
      </H5>
      <pre style={{ maxHeight: 200, overflowY: "scroll" }}>{stateString}</pre>
    </Card>
  );
};
