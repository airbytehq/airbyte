// import { FormattedMessage } from "react-intl";

import { ResizablePanels } from "components/ui/ResizablePanels";
// import { YamlEditor } from "components/YamlEditor";

// import styles from "./ConnectorBuilderPage.module.scss";

export const ConnectorBuilderPage: React.FC = () => {
  return (
    <ResizablePanels
    // leftPanel={{
    //   children: <YamlEditor />,
    //   smallWidthHeader: <FormattedMessage id="connectorBuilder.expandConfiguration" />,
    //   className: styles.leftPanel,
    // }}
    // rightPanel={{
    //   children: <div>Testing panel</div>,
    //   smallWidthHeader: <span>Stream Name</span>,
    //   showPanel: true,
    //   className: styles.rightPanel,
    //   startingFlex: 0.33,
    // }}
    // containerClassName={styles.container}
    />
  );
};
