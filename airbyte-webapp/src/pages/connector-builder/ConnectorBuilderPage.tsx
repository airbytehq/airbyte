import { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectorTestingPanel } from "components/ConnectorTestingPanel";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { YamlEditor } from "components/YamlEditor";

import styles from "./ConnectorBuilderPage.module.scss";

export const ConnectorBuilderPage: React.FC = () => {
  const streamNames = ["Customers", "Users", "Applications"];
  const [selectedStream, setSelectedStream] = useState(streamNames[0]);

  const handleStreamSelection = (selectedStreamName: string) => {
    setSelectedStream(selectedStreamName);
  };

  return (
    <ResizablePanels
      leftPanel={{ children: <YamlEditor />, smallWidthHeader: <FormattedMessage id="builder.expandConfiguration" /> }}
      rightPanel={{
        children: (
          <ConnectorTestingPanel
            streams={streamNames}
            selectedStream={selectedStream}
            onStreamSelect={handleStreamSelection}
          />
        ),
        smallWidthHeader: <span>{selectedStream}</span>,
        showPanel: true,
        className: styles.rightPanel,
      }}
      containerClassName={styles.container}
    />
  );
};
