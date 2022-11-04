import classNames from "classnames";
import { useState } from "react";
import { FormattedMessage } from "react-intl";

import { Paginator } from "components/ui/Paginator";
import { ResizablePanels } from "components/ui/ResizablePanels";
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
    <ResizablePanels
      className={classNames(className, styles.container)}
      orientation="horizontal"
      firstPanel={{
        className: styles.resultContainer,
        children: (
          <>
            {streamRead.slices.length > 1 && (
              <SliceSelector
                className={styles.sliceSelector}
                slices={streamRead.slices}
                selectedSliceIndex={selectedSliceIndex}
                onSelect={setSelectedSliceIndex}
              />
            )}
            <PageDisplay className={styles.pageDisplay} page={page} />
            {slice.pages.length > 1 && (
              <div className={styles.paginator}>
                <Text className={styles.pageLabel}>Page:</Text>
                <Paginator numPages={numPages} onPageChange={handlePageChange} selectedPage={selectedPage} />
              </div>
            )}
          </>
        ),
        minWidth: 120,
      }}
      secondPanel={{
        className: styles.logsContainer,
        children: (
          <>
            <div className={styles.logsHeader}>
              <Text size="sm" bold>
                <FormattedMessage id="connectorBuilder.connectorLogs" />
              </Text>
              <Text className={styles.numLogsDisplay} size="xs" bold>
                {streamRead.logs.length}
              </Text>
            </div>
            <div className={styles.logsDisplay}>
              <pre>{JSON.stringify(streamRead.logs, null, 2)}</pre>
            </div>
          </>
        ),
        minWidth: 30,
        flex: 0,
      }}
    />
  );
};
