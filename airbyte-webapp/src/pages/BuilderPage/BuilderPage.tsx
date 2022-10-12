import { FormattedMessage } from "react-intl";

import { TwoPanelLayout } from "components/ui/TwoPanelLayout";

import styles from "./BuilderPage.module.scss";
import { YamlEditor } from "./components/YamlEditor";

export const BuilderPage: React.FC = () => {
  return (
    <TwoPanelLayout
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
