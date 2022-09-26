import React from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { LoadingButton, Switch } from "components";

import { useEnableConnection } from "hooks/services/useConnectionHook";

interface IProps {
  allowSync?: boolean;
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  onSync: (id: string) => void;
}

const SmallButton = styled(LoadingButton)`
  padding: 6px 8px 7px;
`;

const ProgressMessage = styled.div`
  padding: 7px 0;
`;

const StatusCell: React.FC<IProps> = ({ enabled, isManual, id, isSyncing, onSync, allowSync }) => {
  const { mutateAsync: enableConnection, isLoading } = useEnableConnection();

  const [{ loading }, OnLaunch] = useAsyncFn(async (event: React.SyntheticEvent) => {
    event.stopPropagation();
    onSync(id);
  }, []);

  if (!isManual) {
    const onSwitchChange = async (event: React.SyntheticEvent) => {
      event.stopPropagation();
      await enableConnection({
        connectionId: id,
        enable: !enabled,
      });
    };

    return (
      // this is so we can stop event propagation so the row doesn't receive the click and redirect
      // eslint-disable-next-line jsx-a11y/no-static-element-interactions
      <div
        onClick={(event: React.SyntheticEvent) => event.stopPropagation()}
        onKeyPress={(event: React.SyntheticEvent) => event.stopPropagation()}
      >
        <Switch checked={enabled} onChange={onSwitchChange} disabled={!allowSync} loading={isLoading} />
      </div>
    );
  }

  if (isSyncing) {
    return (
      <ProgressMessage>
        <FormattedMessage id="tables.progress" />
      </ProgressMessage>
    );
  }

  return (
    <SmallButton onClick={OnLaunch} isLoading={loading} disabled={!allowSync || !enabled}>
      <FormattedMessage id="tables.launch" />
    </SmallButton>
  );
};

export default StatusCell;
