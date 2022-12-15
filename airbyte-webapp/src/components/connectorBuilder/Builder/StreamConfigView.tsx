import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";

interface StreamConfigViewProps {
  streamNum: number;
}

export const StreamConfigView: React.FC<StreamConfigViewProps> = ({ streamNum }) => {
  const streamPath = (path: string) => `streams[${streamNum}].${path}`;

  return (
    <BuilderCard>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderField type="text" path={streamPath("name")} label="Stream Name" tooltip="Name of the stream" />
      <BuilderField
        type="text"
        path={streamPath("urlPath")}
        label="Path URL"
        tooltip="Path of the endpoint that this stream represents."
      />
      <BuilderField
        type="array"
        path={streamPath("fieldPointer")}
        label="Field Pointer"
        tooltip="Pointer into the response that should be extracted as the final record"
      />
      <BuilderField
        type="enum"
        path={streamPath("httpMethod")}
        options={["GET", "POST"]}
        label="HTTP Method"
        tooltip="HTTP method to use for requests sent to the API"
      />
    </BuilderCard>
  );
};
