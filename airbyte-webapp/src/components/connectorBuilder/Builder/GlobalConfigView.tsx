import { useIntl } from "react-intl";

import { BuilderCard } from "./BuilderCard";
import { BuilderConfigView } from "./BuilderConfigView";
import { BuilderField } from "./BuilderField";
import { BuilderTitle } from "./BuilderTitle";

export const GlobalConfigView: React.FC = () => {
  const { formatMessage } = useIntl();

  return (
    <BuilderConfigView heading={formatMessage({ id: "connectorBuilder.globalConfiguration" })}>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderTitle path="global.connectorName" label="Connector Name" size="lg" />
      <BuilderCard>
        <BuilderField type="text" path="global.urlBase" label="API URL" tooltip="Base URL of the source API" />
      </BuilderCard>
    </BuilderConfigView>
  );
};
