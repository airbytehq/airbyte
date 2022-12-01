import classnames from "classnames";
import { useIntl } from "react-intl";
import { useToggle } from "react-use";

import { Builder } from "components/connectorBuilder/Builder/Builder";
import { StreamTestingPanel } from "components/connectorBuilder/StreamTestingPanel";
import { YamlEditor } from "components/connectorBuilder/YamlEditor";
import { ResizablePanels } from "components/ui/ResizablePanels";

import { ConnectorBuilderStateProvider } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./ConnectorBuilderPage.module.scss";

const ConnectorBuilderPageInner: React.FC = () => {
  const { formatMessage } = useIntl();
  const [showYamlEditor, toggleYamlEditor] = useToggle(false);

  return (
    <ResizablePanels
      className={classnames({ [styles.gradientBg]: showYamlEditor, [styles.solidBg]: !showYamlEditor })}
      firstPanel={{
        children: (
          <>
            {showYamlEditor ? (
              <YamlEditor toggleYamlEditor={toggleYamlEditor} />
            ) : (
              <Builder toggleYamlEditor={toggleYamlEditor} />
            )}
          </>
        ),
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
