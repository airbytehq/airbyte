import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";

export const GlobalConfigView: React.FC = () => {
  return (
    <>
      <BuilderCard>
        <BuilderField type="text" path="connectorName" label="Connector Name" />
      </BuilderCard>
      <BuilderCard>
        <BuilderField type="text" path="urlBase" label="API URL" />
      </BuilderCard>
    </>
  );
};
