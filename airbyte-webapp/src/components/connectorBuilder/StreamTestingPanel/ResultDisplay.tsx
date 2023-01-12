import classNames from "classnames";

import { Paginator } from "components/ui/Paginator";
import { Text } from "components/ui/Text";

import { StreamReadSlicesItem } from "core/request/ConnectorBuilderClient";
import { useSelectedPageAndSlice } from "services/connectorBuilder/ConnectorBuilderStateService";

import { PageDisplay } from "./PageDisplay";
import styles from "./ResultDisplay.module.scss";
import { SliceSelector } from "./SliceSelector";

interface ResultDisplayProps {
  slices: StreamReadSlicesItem[];
  className?: string;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ slices, className }) => {
  const { selectedSlice, selectedPage, setSelectedSlice, setSelectedPage } = useSelectedPageAndSlice();

  const slice = slices[selectedSlice];
  const numPages = slice.pages.length;
  const page = slice.pages[selectedPage];

  return (
    <div className={classNames(className, styles.container)}>
      {slices.length > 1 && (
        <SliceSelector
          className={styles.sliceSelector}
          slices={slices}
          selectedSliceIndex={selectedSlice}
          onSelect={setSelectedSlice}
        />
      )}
      <PageDisplay className={styles.pageDisplay} page={page} />
      {slice.pages.length > 1 && (
        <div className={styles.paginator}>
          <Text className={styles.pageLabel}>Page:</Text>
          <Paginator numPages={numPages} onPageChange={setSelectedPage} selectedPage={selectedPage} />
        </div>
      )}
    </div>
  );
};
