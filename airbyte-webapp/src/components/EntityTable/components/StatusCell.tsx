import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Toggle from "components/Toggle";
import Button from "components/Button";

type IProps = {
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  onChangeStatus: (id: string) => void;
  onSync: (id: string) => void;
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
  id,
  onChangeStatus,
  isSyncing,
  onSync,
}) => {
  const OnLaunch = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    onSync(id);
  };

  const OnToggleClick = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    onChangeStatus(id);
  };

  if (!isManual) {
    return <Toggle checked={enabled} onChange={OnToggleClick} />;
  }

  if (isSyncing) {
    return (
      <ProgressMessage>
        <FormattedMessage id="tables.progress" />
      </ProgressMessage>
    );
  }

  return (
    <SmallButton onClick={OnLaunch}>
      <FormattedMessage id="tables.launch" />
    </SmallButton>
  );
};

export default StatusCell;
