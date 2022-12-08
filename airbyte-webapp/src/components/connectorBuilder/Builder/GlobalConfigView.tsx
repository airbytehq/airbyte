import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";

export const GlobalConfigView: React.FC = () => {
  return (
    <>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderCard>
        <BuilderField
          type="text"
          path="global.connectorName"
          label="Connector Name"
          tooltip="Name of the connector being built"
        />
      </BuilderCard>
      <BuilderCard>
        <BuilderField type="text" path="global.urlBase" label="API URL" tooltip="Base URL of the source API" />
      </BuilderCard>
    </>
  );
};
