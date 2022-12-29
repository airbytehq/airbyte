import classNames from "classnames";
import { useState } from "react";

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

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ streamRead, className }) => {
  const [selectedSliceIndex, setSelectedSliceIndex] = useState(0);
  const [selectedPage, setSelectedPage] = useState(0);

  const handlePageChange = (selectedPageIndex: number) => {
    setSelectedPage(selectedPageIndex);
  };

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
        <Paginator numPages={numPages} onPageChange={handlePageChange} selectedPage={selectedPage} />
      </div>
    </div>
  );
};
