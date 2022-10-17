import { useState } from "react";
import { FormattedMessage } from "react-intl";

import { ConnectorTestingPanel } from "components/ConnectorTestingPanel";
import { ResizablePanels } from "components/ui/ResizablePanels";
import { YamlEditor } from "components/YamlEditor";

import styles from "./ConnectorBuilderPage.module.scss";

export const ConnectorBuilderPage: React.FC = () => {
  const urlBase = "https://my.url.api.com";
  const streams = [
    { name: "Customers", url: `${urlBase}/customers` },
    { name: "Users", url: `${urlBase}/users` },
    { name: "Applications", url: `${urlBase}/applications` },
  ];
  const [selectedStream, setSelectedStream] = useState(streams[0].name);

  const handleStreamSelection = (selectedStreamName: string) => {
    setSelectedStream(selectedStreamName);
  };

  return (
    <ResizablePanels
      leftPanel={{
        children: <YamlEditor />,
        smallWidthHeader: <FormattedMessage id="connectorBuilder.expandConfiguration" />,
        className: styles.leftPanel,
      }}
      rightPanel={{
        children: (
          <ConnectorTestingPanel
            streams={streams}
            selectedStream={selectedStream}
            onStreamSelect={handleStreamSelection}
          />
        ),
        smallWidthHeader: <span>{selectedStream}</span>,
        showPanel: true,
        className: styles.rightPanel,
        startingFlex: 0.33,
      }}
      containerClassName={styles.container}
    />
  );
};
