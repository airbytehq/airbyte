import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useAsyncFn } from "react-use";

import { LoadingButton, Toggle } from "components";

type IProps = {
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  onChangeStatus: (id: string) => void;
  onSync: (id: string) => void;
};

const SmallButton = styled(LoadingButton)`
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
  const [{ loading }, OnLaunch] = useAsyncFn(
    async (event: React.SyntheticEvent) => {
      event.stopPropagation();
      await onSync(id);
    },
    []
  );

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
    <SmallButton onClick={OnLaunch} isLoading={loading}>
      <FormattedMessage id="tables.launch" />
    </SmallButton>
  );
};

export default StatusCell;
