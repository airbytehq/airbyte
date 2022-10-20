import { FormattedMessage } from "react-intl";

import { ConnectorTestingPanel } from "components/ConnectorTestingPanel";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { YamlEditor } from "components/YamlEditor";

import { useConnectorBuilderState } from "services/connector-builder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";

export const ConnectorBuilderPage: React.FC = () => {
  const { selectedStream } = useConnectorBuilderState();

  return (
    <ResizablePanels
      leftPanel={{
        children: <YamlEditor />,
        smallWidthHeader: <FormattedMessage id="connectorBuilder.expandConfiguration" />,
        className: styles.leftPanel,
      }}
      rightPanel={{
        children: <ConnectorTestingPanel />,
        smallWidthHeader: <span>{selectedStream.name}</span>,
        showPanel: true,
        className: styles.rightPanel,
        startingFlex: 0.33,
      }}
      containerClassName={styles.container}
    />
  );
};
