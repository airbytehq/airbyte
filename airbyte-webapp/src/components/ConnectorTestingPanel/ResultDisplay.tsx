import { Text } from "components/ui/Text";

import { StreamRead } from "core/request/ConnectorBuilderClient";

import styles from "./ResultDisplay.module.scss";

interface ResultDisplayProps {
  data: StreamRead;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ data }) => {
  console.log(JSON.stringify(data));

  return (
    <div>
      {data.slices.map((slice) => (
        <div className={styles.slice}>
          <Text>{`Slice ${JSON.stringify(slice.sliceDescriptor)}`}</Text>
          {slice.pages.map((page, pageNumber) => (
            <div className={styles.page}>
              <Text>{`Page ${pageNumber}`}</Text>
              <div className={styles.dataObject}>{`Request: ${JSON.stringify(page.request)}`}</div>
              <div className={styles.dataObject}>{`Response: ${JSON.stringify(page.response)}`}</div>
              <div className={styles.dataObject}>{`Airbyte Messages: ${JSON.stringify(page.airbyteMessages)}`}</div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
