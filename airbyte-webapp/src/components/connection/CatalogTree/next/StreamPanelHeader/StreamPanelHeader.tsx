import { FormattedMessage } from "react-intl";

import { CrossIcon } from "components/icons/CrossIcon";
import { Button } from "components/ui/Button";
import { Switch } from "components/ui/Switch";

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
  value?: string;
}

export const StreamProperty: React.FC<SomethingProps> = ({ messageId, value }) => {
  return (
    <span>
      <strong>
        <FormattedMessage id={messageId} />
      </strong>
      : {value}
    </span>
  );
};

export const StreamPanelHeader: React.FC<StreamPanelHeaderProps> = ({
  config,
  disabled,
  onClose,
  onSelectedChange,
  stream,
}) => {
  return (
    <div className={styles.container}>
      <div>
        <Switch small checked={config?.selected} onChange={onSelectedChange} disabled={disabled} />
      </div>
      <div className={styles.properties}>
        <StreamProperty messageId="form.namespace" value={stream?.namespace} />
        <StreamProperty messageId="form.streamName" value={stream?.name} />
        <StreamProperty messageId="form.syncMode" value={config?.syncMode} />
      </div>
      <Button variant="clear" onClick={onClose} icon={<CrossIcon />} />
    </div>
  );
};
