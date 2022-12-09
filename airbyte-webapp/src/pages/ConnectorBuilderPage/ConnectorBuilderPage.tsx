import { useIntl } from "react-intl";

import { StreamTestingPanel } from "components/connectorBuilder/StreamTestingPanel";
import { YamlEditor } from "components/connectorBuilder/YamlEditor";
import { ResizablePanels } from "components/ui/ResizablePanels";

import { ConnectorBuilderStateProvider } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";

const ConnectorBuilderPageInner: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <ResizablePanels
      className={styles.container}
      firstPanel={{
        children: <YamlEditor />,
        className: styles.leftPanel,
        minWidth: 100,
      }}
      secondPanel={{
        children: <StreamTestingPanel />,
        className: styles.rightPanel,
        flex: 0.33,
        minWidth: 60,
        overlay: {
          displayThreshold: 325,
          header: formatMessage({ id: "connectorBuilder.testConnector" }),
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
