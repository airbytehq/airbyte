import React, { useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { H5, Card } from "components";

import { ConnectionState } from "core/request/AirbyteClient";
import { useGetConnectionState } from "hooks/services/useConnectionHook";

interface StateBlockProps {
  connectionId: string;
}

export const StateBlock: React.FC<StateBlockProps> = ({ connectionId }) => {
  const { formatMessage } = useIntl();
  const state = useGetConnectionState(connectionId);

  const stateString = useMemo(
    () => displayState(state.state, state.globalState, state.streamState, formatMessage),
    [formatMessage, state.state, state.globalState, state.streamState]
  );

  return (
    <Card $withPadding>
      <H5 bold>
        <FormattedMessage id="tables.connectionState.title" />
      </H5>
      <pre style={{ maxHeight: 200, overflowY: "scroll" }}>{stateString}</pre>
    </Card>
  );
};

function displayState(
  legacyState: ConnectionState["state"],
  globalState: ConnectionState["globalState"],
  streamState: ConnectionState["streamState"],
  formatMessage: ReturnType<typeof useIntl>["formatMessage"]
) {
  // This hierarchy assumes that for those connections which have both global and per-stream state, the global state contains a meaningful copy of any state which would also be saved per-stream
  const displayState = legacyState ?? globalState ?? streamState ?? null;
  return displayState
    ? JSON.stringify(displayState, null, 2)
    : formatMessage({ id: "tables.connectionState.noConnectionState" });
}
