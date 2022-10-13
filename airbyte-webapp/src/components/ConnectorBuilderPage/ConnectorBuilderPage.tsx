import { FormattedMessage } from "react-intl";

import { ResizablePanels } from "components/ui/ResizablePanels";

import styles from "./ConnectorBuilderPage.module.scss";
import { YamlEditor } from "./YamlEditor";

export const ConnectorBuilderPage: React.FC = () => {
  return (
    <ResizablePanels
      leftPanel={{ children: <YamlEditor />, smallWidthHeader: <FormattedMessage id="builder.expandConfiguration" /> }}
      rightPanel={{
        children: <p>Testing Panel</p>,
        smallWidthHeader: <span>Stream name</span>,
        showPanel: true,
        className: styles.rightPanel,
      }}
      containerClassName={styles.container}
    />
  );
};
