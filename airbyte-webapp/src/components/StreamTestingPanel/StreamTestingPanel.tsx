import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { ConfigMenu } from "./ConfigMenu";
import { StreamSelector } from "./StreamSelector";
import { StreamTester } from "./StreamTester";
import styles from "./StreamTestingPanel.module.scss";

export const StreamTestingPanel: React.FC<unknown> = () => {
  const { selectedStream } = useConnectorBuilderState();

  return (
    <div className={styles.container}>
      <ConfigMenu />
      <StreamSelector className={styles.streamSelector} />
      <StreamTester selectedStream={selectedStream} />
    </div>
  );
};
