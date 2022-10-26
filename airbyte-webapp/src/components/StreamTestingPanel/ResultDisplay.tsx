import classNames from "classnames";
import { useState } from "react";

import { Paginator } from "components/ui/Paginator";
import { Text } from "components/ui/Text";

import { StreamRead } from "core/request/ConnectorBuilderClient";

import styles from "./ResultDisplay.module.scss";

interface ResultDisplayProps {
  streamRead: StreamRead;
  className?: string;
}

const marginPagesDisplayed = 2;

// this keeps the number of elements displayed constant regardless of which page is selected
function pageRangeDisplayed(numPages: number, selectedPageIndex: number): number {
  if (selectedPageIndex === 0 || numPages - selectedPageIndex <= 3) {
    return 6;
  } else if (selectedPageIndex === 1 || selectedPageIndex === 2) {
    return 5;
  } else if (selectedPageIndex === 3 || numPages - selectedPageIndex === 4) {
    return 4;
  }
  return 3;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ streamRead, className }) => {
  const [selectedPage, setSelectedPage] = useState(0);

  const handlePageChange = (selectedPageIndex: number) => {
    console.log(selectedPageIndex);
    setSelectedPage(selectedPageIndex);
  };

  if (streamRead.slices.length === 0) {
    return <div>Click Test to fetch data!</div>;
  }

  console.log(selectedPage);

  const slice = streamRead.slices[0];
  const numPages = slice.pages.length;
  const page = slice.pages[selectedPage];

  return (
    <div className={classNames(className, styles.container)}>
      <div className={classNames(styles.displayBox, styles.slice)}>
        <Text>{`Slice ${JSON.stringify(slice.sliceDescriptor)}`}</Text>
        <Text>{`Page ${selectedPage + 1}`}</Text>
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

        {/* {slice.pages.map((page, pageNumber) => (
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
        ))} */}
        {/* {slice.state && (
          <div className={classNames(styles.displayBox, styles.state)}>
            State:
            <pre>{JSON.stringify(slice.state, null, 2)}</pre>
          </div>
        )} */}
      </div>
      {/* {streamRead.logs.length > 0 && (
        <div className={classNames(styles.displayBox, styles.logs)}>
          Logs:
          <pre>{JSON.stringify(streamRead.logs, null, 2)}</pre>
        </div>
      )} */}
      <div className={styles.paginator}>
        <Text className={styles.pageLabel}>Page:</Text>
        <Paginator
          numPages={numPages}
          onPageChange={handlePageChange}
          marginPagesDisplayed={marginPagesDisplayed}
          pageRangeDisplayed={pageRangeDisplayed(numPages, selectedPage)}
        />
      </div>
    </div>
  );
};
