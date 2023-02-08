import React, { ReactNode } from "react";
import { FormattedMessage } from "react-intl";

import { CrossIcon } from "components/icons/CrossIcon";
import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Switch } from "components/ui/Switch";
import { Text } from "components/ui/Text";

import { AirbyteStream, AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import styles from "./StreamPanelHeader.module.scss";

interface StreamPanelHeaderProps {
  config?: AirbyteStreamConfiguration;
  disabled?: boolean;
  onClose: () => void;
  onSelectedChange: () => void;
  stream?: AirbyteStream;
}

interface SomethingProps {
  messageId: string;
  value?: string | ReactNode;
}

export const StreamProperty: React.FC<SomethingProps> = ({ messageId, value }) => (
  <span>
    <Text size="sm" className={styles.streamPropLabel}>
      <FormattedMessage id={messageId} />
    </Text>
    <Text size="md" className={styles.streamPropValue}>
      {value}
    </Text>
  </span>
);

export const StreamPanelHeader: React.FC<StreamPanelHeaderProps> = ({
  config,
  disabled,
  onClose,
  onSelectedChange,
  stream,
}) => {
  const syncMode = (
    <>
      <FormattedMessage id={`syncMode.${config?.syncMode}`} />
      {` | `}
      <FormattedMessage id={`destinationSyncMode.${config?.destinationSyncMode}`} />
    </>
  );
  return (
    <FlexContainer className={styles.container} justifyContent="space-between" alignItems="center">
      <FlexContainer gap="md" alignItems="center" className={styles.leftActions}>
        <Switch size="sm" checked={config?.selected} onChange={onSelectedChange} disabled={disabled} />
        <Text color="grey-300" size="xs">
          <FormattedMessage id="form.stream.sync" />
        </Text>
      </FlexContainer>
      <FlexContainer className={styles.properties} justifyContent="center" gap="xl">
        <StreamProperty
          messageId="form.namespace"
          value={stream?.namespace ?? <FormattedMessage id="form.noNamespace" />}
        />
        <StreamProperty messageId="form.streamName" value={stream?.name} />
        <StreamProperty messageId="form.syncMode" value={syncMode} />
      </FlexContainer>
      <FlexContainer className={styles.rightActions} justifyContent="flex-end">
        <Button variant="clear" onClick={onClose} className={styles.crossIcon} icon={<CrossIcon />} />
      </FlexContainer>
    </FlexContainer>
  );
};
