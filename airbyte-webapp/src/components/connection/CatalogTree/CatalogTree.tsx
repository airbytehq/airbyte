import classNames from "classnames";
import React, { useCallback, useMemo, useState } from "react";

import { LoadingBackdrop } from "components/ui/LoadingBackdrop";

import { SyncSchemaStream } from "core/domain/catalog";
import { useNewTableDesignExperiment } from "hooks/connection/useNewTableDesignExperiment";
import { BulkEditServiceProvider } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { naturalComparatorBy } from "utils/objects";

import styles from "./CatalogTree.module.scss";
import { CatalogTreeBody } from "./CatalogTreeBody";
import { CatalogTreeSearch } from "./CatalogTreeSearch";
import { BulkEditPanel } from "./next/BulkEditPanel";

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
  const isNewTableDesignEnabled = useNewTableDesignExperiment();
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
      streams.filter((stream) => {
        const matchingInitialValue = initialValues.syncCatalog.streams.find((initialStream) => {
          if (!stream.stream || !initialStream.stream) {
            return false;
          }

          return (
            initialStream.stream.name === stream.stream.name &&
            initialStream.stream.namespace === stream.stream.namespace
          );
        });
        return stream.config?.selected !== matchingInitialValue?.config?.selected;
      }),
    [initialValues.syncCatalog.streams, streams]
  );

  return (
    <BulkEditServiceProvider nodes={streams} update={onStreamsChanged}>
      <LoadingBackdrop loading={isLoading}>
        {mode !== "readonly" && <CatalogTreeSearch onSearch={setSearchString} />}
        <div className={classNames(styles.catalogTreeTable, { [styles.newCatalogTreeTable]: isNewTableDesignEnabled })}>
          <CatalogTreeBody
            streams={filteredStreams}
            changedStreams={changedStreams}
            onStreamChanged={onSingleStreamChanged}
          />
        </div>
      </LoadingBackdrop>
      {isNewTableDesignEnabled && <BulkEditPanel />}
    </BulkEditServiceProvider>
  );
};

export const CatalogTree = React.memo(CatalogTreeComponent);
