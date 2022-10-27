import classNames from "classnames";
import { useState } from "react";
import { useIntl } from "react-intl";

import { Paginator } from "components/ui/Paginator";
import { Text } from "components/ui/Text";

import { StreamRead } from "core/request/ConnectorBuilderClient";

import { PageDisplay } from "./PageDisplay";
import styles from "./ResultDisplay.module.scss";
import { SliceSelector } from "./SliceSelector";

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
  const { formatMessage } = useIntl();
  const [selectedSliceIndex, setSelectedSliceIndex] = useState(0);
  const [selectedPage, setSelectedPage] = useState(0);

  const handlePageChange = (selectedPageIndex: number) => {
    console.log(selectedPageIndex);
    setSelectedPage(selectedPageIndex);
  };

  if (streamRead.slices.length === 0) {
    return <div className={styles.placeholder}>{formatMessage({ id: "connectorBuilder.resultsPlaceholder" })}</div>;
  }

  const slice = streamRead.slices[selectedSliceIndex];
  const numPages = slice.pages.length;
  const page = slice.pages[selectedPage];

  return (
    <div className={classNames(className, styles.container)}>
      <SliceSelector
        className={styles.sliceSelector}
        slices={streamRead.slices}
        selectedSliceIndex={selectedSliceIndex}
        onSelect={setSelectedSliceIndex}
      />
      <PageDisplay className={styles.pageDisplay} page={page} />
      <div className={styles.paginator}>
        <Text className={styles.pageLabel}>Page:</Text>
        <Paginator
          forcePage={selectedPage}
          numPages={numPages}
          onPageChange={handlePageChange}
          marginPagesDisplayed={marginPagesDisplayed}
          pageRangeDisplayed={pageRangeDisplayed(numPages, selectedPage)}
        />
      </div>
    </div>
  );
};
