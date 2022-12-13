import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";

import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderTitle } from "./BuilderTitle";
import styles from "./StreamConfigView.module.scss";

interface StreamConfigViewProps {
  streamNum: number;
}

export const StreamConfigView: React.FC<StreamConfigViewProps> = ({ streamNum }) => {
  const streamPath = (path: string) => `streams[${streamNum}].${path}`;

  return (
    <div className={styles.container}>
      <Heading className={styles.heading} as="h1" size="sm">
        <FormattedMessage id="connectorBuilder.stream" />
      </Heading>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderTitle path={streamPath("name")} label="Stream Name" size="md" />
      <BuilderCard>
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
    </div>
  );
};
