import React from "react";
import { FormattedMessage } from "react-intl";

import Toggle from "../../../../../components/Toggle";
import Button from "../../../../../components/Button";
import styled from "styled-components";

type IProps = {
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  connectionId: string;
  onChangeStatus: (connectionId: string) => void;
  onSync: (connectionId: string) => void;
};

const SmallButton = styled(Button)`
  padding: 6px 8px 7px;
`;

const ProgressMessage = styled.div`
  padding: 7px 0;
`;

const StatusCell: React.FC<IProps> = ({
  enabled,
  isManual,
  connectionId,
  onChangeStatus,
  isSyncing,
  onSync
}) => {
  const OnLaunch = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    onSync(connectionId);
  };

  const OnToggleClick = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    onChangeStatus(connectionId);
  };

  if (!isManual) {
    return <Toggle checked={enabled} onChange={OnToggleClick} />;
  }

  if (isSyncing) {
    return (
      <ProgressMessage>
        <FormattedMessage id="sources.progress" />
      </ProgressMessage>
    );
  }

  return (
    <SmallButton onClick={OnLaunch}>
      <FormattedMessage id="sources.launch" />
    </SmallButton>
  );
};

export default StatusCell;
