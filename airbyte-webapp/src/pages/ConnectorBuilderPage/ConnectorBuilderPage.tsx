import { capitalize } from "lodash";

import { StreamTestingPanel } from "components/StreamTestingPanel";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { YamlEditor } from "components/YamlEditor";

import {
  ConnectorBuilderStateProvider,
  useConnectorBuilderState,
} from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";

const ConnectorBuilderPageInner: React.FC = () => {
  const { selectedStream } = useConnectorBuilderState();

  return (
    <ResizablePanels
      className={styles.container}
      leftPanel={{
        children: <YamlEditor />,
        className: styles.leftPanel,
        minWidth: 400,
      }}
      rightPanel={{
        children: <StreamTestingPanel />,
        className: styles.rightPanel,
        startingFlex: 0.33,
        minWidth: 60,
        overlay: {
          displayThreshold: 300,
          header: capitalize(selectedStream.name),
          rotation: "counter-clockwise",
        },
      }}
    />
  );
};

export const ConnectorBuilderPage: React.FC = () => (
  <ConnectorBuilderStateProvider>
    <ConnectorBuilderPageInner />
  </ConnectorBuilderStateProvider>
);
