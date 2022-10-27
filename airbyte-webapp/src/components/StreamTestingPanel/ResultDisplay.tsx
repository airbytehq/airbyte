import classNames from "classnames";
import { useState } from "react";

import { Paginator } from "components/ui/Paginator";
import { Text } from "components/ui/Text";

import { StreamRead } from "core/request/ConnectorBuilderClient";

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
  const [selectedPage, setSelectedPage] = useState(0);

  const handlePageChange = (selectedPageIndex: number) => {
    console.log(selectedPageIndex);
    setSelectedPage(selectedPageIndex);
  };

  if (streamRead.slices.length === 0) {
    return <div>Click Test to fetch data!</div>;
  }

  const slice = streamRead.slices[0];
  const numPages = slice.pages.length;
  // const page = slice.pages[selectedPage];

  return (
    <div className={classNames(className, styles.container)}>
      <SliceSelector slices={streamRead.slices} />
      {/* <PageDisplay page={page} /> */}
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
