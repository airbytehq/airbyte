import React from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { LoadingButton, Switch } from "components";

type IProps = {
  allowSync?: boolean;
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

const StatusCell: React.FC<IProps> = ({ enabled, isManual, id, onChangeStatus, isSyncing, onSync, allowSync }) => {
  const [{ loading }, OnLaunch] = useAsyncFn(async (event: React.SyntheticEvent) => {
    event.stopPropagation();
    await onSync(id);
  }, []);

  const OnToggleClick = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    onChangeStatus(id);
  };

  if (!isManual) {
    // Getting the loading state down here may be difficult.
    // ConnectionsTable.tsx#28
    // The data is invalidated, then re-loaded. There's no specific action flow for loading.
    return <Switch checked={enabled} onChange={OnToggleClick} disabled={!allowSync} />;
  }

  if (isSyncing) {
    return (
      <ProgressMessage>
        <FormattedMessage id="tables.progress" />
      </ProgressMessage>
    );
  }

  return (
    <SmallButton onClick={OnLaunch} isLoading={loading} disabled={!allowSync}>
      <FormattedMessage id="tables.launch" />
    </SmallButton>
  );
};

export default StatusCell;
