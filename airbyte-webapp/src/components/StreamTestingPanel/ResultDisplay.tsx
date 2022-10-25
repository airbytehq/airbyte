import classNames from "classnames";

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
        <div className={classNames(styles.displayBox, styles.container, styles.slice)}>
          <Text>{`Slice ${JSON.stringify(slice.sliceDescriptor)}`}</Text>
          {slice.pages.map((page, pageNumber) => (
            <div className={classNames(styles.displayBox, styles.container, styles.page)}>
              <Text>{`Page ${pageNumber}`}</Text>
              <div className={classNames(styles.displayBox, styles.pageData)}>
                Request:
                <pre>{JSON.stringify(page.request, null, 2)}</pre>
              </div>
              <div className={classNames(styles.displayBox, styles.pageData)}>
                Response:
                <pre>{JSON.stringify(page.response, null, 2)}</pre>
              </div>
              <div className={classNames(styles.displayBox, styles.pageData)}>
                Records:
                <pre>{JSON.stringify(page.records, null, 2)}</pre>
              </div>
            </div>
          ))}
          {slice.state && (
            <div className={classNames(styles.displayBox, styles.state)}>
              State:
              <pre>{JSON.stringify(slice.state, null, 2)}</pre>
            </div>
          )}
        </div>
      ))}
      {data.logs.length > 0 && (
        <div className={classNames(styles.displayBox, styles.logs)}>
          Logs:
          <pre>{JSON.stringify(data.logs, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
