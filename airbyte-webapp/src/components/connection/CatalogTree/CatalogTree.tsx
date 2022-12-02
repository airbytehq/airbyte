import React, { useCallback, useMemo, useState } from "react";

import { LoadingBackdrop } from "components/ui/LoadingBackdrop";

import { SyncSchemaStream } from "core/domain/catalog";
import { BulkEditServiceProvider } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { naturalComparatorBy } from "utils/objects";

import { BulkHeader } from "./BulkHeader";
import styles from "./CatalogTree.module.scss";
import { CatalogTreeBody } from "./CatalogTreeBody";
import { CatalogTreeHeader } from "./CatalogTreeHeader";
import { CatalogTreeSearch } from "./CatalogTreeSearch";
import { CatalogTreeSubheader } from "./CatalogTreeSubheader";
import { BulkEditPanel } from "./next/BulkEditPanel";
import { CatalogTreeTableHeader } from "./next/CatalogTreeTableHeader";
import { StreamConnectionHeader } from "./next/StreamConnectionHeader";

interface CatalogTreeProps {
  streams: SyncSchemaStream[];
  onStreamsChanged: (streams: SyncSchemaStream[]) => void;
  isLoading: boolean;
}

const CatalogTreeComponent: React.FC<React.PropsWithChildren<CatalogTreeProps>> = ({
  streams,
  onStreamsChanged,
  isLoading,
}) => {
  const isNewStreamsTableEnabled = process.env.REACT_APP_NEW_STREAMS_TABLE ?? false;
  const { initialValues, mode } = useConnectionFormService();

  const [searchString, setSearchString] = useState("");

  const onSingleStreamChanged = useCallback(
    (newValue: SyncSchemaStream) => onStreamsChanged(streams.map((str) => (str.id === newValue.id ? newValue : str))),
    [streams, onStreamsChanged]
  );

  const sortedSchema = useMemo(
    () => [...streams].sort(naturalComparatorBy((syncStream) => syncStream.stream?.name ?? "")),
    [streams]
  );

  const filteredStreams = useMemo(() => {
    const filters: Array<(s: SyncSchemaStream) => boolean> = [
      (_: SyncSchemaStream) => true,
      searchString
        ? (stream: SyncSchemaStream) => stream.stream?.name.toLowerCase().includes(searchString.toLowerCase())
        : null,
    ].filter(Boolean) as Array<(s: SyncSchemaStream) => boolean>;

    return sortedSchema.filter((stream) => filters.every((f) => f(stream)));
  }, [searchString, sortedSchema]);

  const changedStreams = useMemo(
    () =>
      streams.filter((stream, idx) => {
        return stream.config?.selected !== initialValues.syncCatalog.streams[idx].config?.selected;
      }),
    [initialValues.syncCatalog.streams, streams]
  );

  return (
    <BulkEditServiceProvider nodes={streams} update={onStreamsChanged}>
      <LoadingBackdrop loading={isLoading}>
        {mode !== "readonly" && <CatalogTreeSearch onSearch={setSearchString} />}
        <div className={isNewStreamsTableEnabled ? undefined : styles.catalogTreeTable}>
          {isNewStreamsTableEnabled ? (
            <>
              <StreamConnectionHeader />
              <CatalogTreeTableHeader />
            </>
          ) : (
            <>
              <CatalogTreeHeader />
              <CatalogTreeSubheader />
              <BulkHeader />
            </>
          )}
          <CatalogTreeBody
            streams={filteredStreams}
            changedStreams={changedStreams}
            onStreamChanged={onSingleStreamChanged}
          />
        </div>
      </LoadingBackdrop>
      {isNewStreamsTableEnabled && <BulkEditPanel />}
    </BulkEditServiceProvider>
  );
};

export const CatalogTree = React.memo(CatalogTreeComponent);
