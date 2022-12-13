import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";

import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderTitle } from "./BuilderTitle";
import styles from "./GlobalConfigView.module.scss";

export const GlobalConfigView: React.FC = () => {
  return (
    <div className={styles.container}>
      <Heading className={styles.heading} as="h1" size="sm">
        <FormattedMessage id="connectorBuilder.globalConfiguration" />
      </Heading>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderTitle path="global.connectorName" label="Connector Name" size="lg" />
      <BuilderCard>
        <BuilderField type="text" path="global.urlBase" label="API URL" tooltip="Base URL of the source API" />
      </BuilderCard>
    </div>
  );
};
