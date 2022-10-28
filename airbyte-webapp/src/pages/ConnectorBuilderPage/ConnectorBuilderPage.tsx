import { ResizablePanels } from "components/ui/ResizablePanels";
import { YamlEditor } from "components/YamlEditor";

import styles from "./ConnectorBuilderPage.module.scss";

export const ConnectorBuilderPage: React.FC = () => {
  return (
    <ResizablePanels
      className={styles.container}
      leftPanel={{
        children: <YamlEditor />,
        className: styles.leftPanel,
        minWidth: 400,
      }}
      rightPanel={{
        children: <div>Testing panel</div>,
        className: styles.rightPanel,
        startingFlex: 0.33,
        minWidth: 60,
        overlay: {
          displayThreshold: 300,
          header: "Stream Name",
          rotation: "counter-clockwise",
        },
      }}
    />
  );
};
