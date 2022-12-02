import React from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { Switch } from "components/ui/Switch";

import { SchemaChange } from "core/request/AirbyteClient";
import { useEnableConnection } from "hooks/services/useConnectionHook";

import { ChangesStatusIcon } from "./ChangesStatusIcon";
import styles from "./StatusCell.module.scss";

interface IProps {
  allowSync?: boolean;
  hasBreakingChange?: boolean;
  enabled?: boolean;
  isSyncing?: boolean;
  isManual?: boolean;
  id: string;
  onSync: (id: string) => void;
  schemaChange: SchemaChange;
}

const ProgressMessage = styled.div`
  padding: 7px 0;
`;

export const StatusCell: React.FC<IProps> = ({
  enabled,
  isManual,
  id,
  isSyncing,
  onSync,
  allowSync,
  schemaChange,
  hasBreakingChange,
}) => {
  const { mutateAsync: enableConnection, isLoading } = useEnableConnection();
  const isSchemaChangesFeatureEnabled = process.env.REACT_APP_AUTO_DETECT_SCHEMA_CHANGES_FEATURE_ENABLED === "true";
  const [{ loading }, OnLaunch] = useAsyncFn(
    async (event: React.SyntheticEvent) => {
      event.stopPropagation();
      onSync(id);
    },
    [id]
  );
  let ControlComponent;

  if (!isManual) {
    const onSwitchChange = async (event: React.SyntheticEvent) => {
      event.stopPropagation();
      await enableConnection({
        connectionId: id,
        enable: !enabled,
      });
    };

    ControlComponent = (
      // this is so we can stop event propagation so the row doesn't receive the click and redirect
      // eslint-disable-next-line jsx-a11y/no-static-element-interactions
      <div
        onClick={(event: React.SyntheticEvent) => event.stopPropagation()}
        onKeyPress={(event: React.SyntheticEvent) => event.stopPropagation()}
      >
        <Switch
          checked={enabled}
          onChange={onSwitchChange}
          disabled={!allowSync || hasBreakingChange}
          loading={isLoading}
          data-testid="enable-connection-switch"
        />
      </div>
    );
  } else if (isSyncing) {
    ControlComponent = (
      <ProgressMessage>
        <FormattedMessage id="tables.progress" />
      </ProgressMessage>
    );
  } else {
    ControlComponent = (
      <Button
        size="xs"
        onClick={OnLaunch}
        isLoading={loading}
        disabled={!allowSync || !enabled || hasBreakingChange}
        data-testid="manual-sync-button"
      >
        <FormattedMessage id="tables.launch" />
      </Button>
    );
  }

  return (
    <div className={styles.container}>
      {ControlComponent}
      {isSchemaChangesFeatureEnabled && <ChangesStatusIcon schemaChange={schemaChange} />}
    </div>
  );
};
