import React from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { Switch } from "components/ui/Switch";

import { useEnableConnection } from "hooks/services/useConnectionHook";

interface IProps {
  allowSync?: boolean;
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  onSync: (id: string) => void;
}

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
    <Button size="xs" onClick={OnLaunch} isLoading={loading} disabled={!allowSync || !enabled}>
      <FormattedMessage id="tables.launch" />
    </Button>
  );
};

export default StatusCell;
