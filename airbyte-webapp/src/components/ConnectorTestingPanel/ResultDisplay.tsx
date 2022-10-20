import { Text } from "components/ui/Text";

import { StreamRead } from "core/request/ConnectorBuilderClient";

import styles from "./ResultDisplay.module.scss";

interface ResultDisplayProps {
  data: StreamRead;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ data }) => {
  console.log(JSON.stringify(data));

  return (
    <div className={styles.container}>
      {data.slices.map((slice) => (
        <div className={styles.slice}>
          <Text>{`Slice ${JSON.stringify(slice.sliceDescriptor)}`}</Text>
          {slice.pages.map((page, pageNumber) => (
            <div className={styles.page}>
              <Text>{`Page ${pageNumber}`}</Text>
              <div className={styles.dataObject}>
                Request:
                <pre>{JSON.stringify(page.request, null, 2)}</pre>
              </div>
              <div className={styles.dataObject}>
                Response:
                <pre>{JSON.stringify(page.response, null, 2)}</pre>
              </div>
              <div className={styles.dataObject}>
                Airbyte Messages:
                <pre>{JSON.stringify(page.airbyteMessages, null, 2)}</pre>
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};
