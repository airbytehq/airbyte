import React, { useCallback, useMemo, useState } from "react";

import { LoadingBackdrop } from "components/ui/LoadingBackdrop";

import { SyncSchemaStream } from "core/domain/catalog";
import { BulkEditServiceProvider } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { naturalComparatorBy } from "utils/objects";

import { BulkHeader } from "./BulkHeader";
import { CatalogTreeBody } from "./CatalogTreeBody";
import { CatalogTreeHeader } from "./CatalogTreeHeader";
import { CatalogTreeSearch } from "./CatalogTreeSearch";
import { CatalogTreeSubheader } from "./CatalogTreeSubheader";

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
  const { mode } = useConnectionFormService();

  const [searchString, setSearchString] = useState("");

  const onSingleStreamChanged = useCallback(
    (newValue: SyncSchemaStream) => onStreamsChanged(streams.map((str) => (str.id === newValue.id ? newValue : str))),
    [streams, onStreamsChanged]
  );

  const sortedSchema = useMemo(
    () => streams.sort(naturalComparatorBy((syncStream) => syncStream.stream?.name ?? "")),
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

  return (
    <BulkEditServiceProvider nodes={streams} update={onStreamsChanged}>
      <LoadingBackdrop loading={isLoading}>
        {mode !== "readonly" && <CatalogTreeSearch onSearch={setSearchString} />}
        <CatalogTreeHeader />
        <CatalogTreeSubheader />
        <BulkHeader />
        <CatalogTreeBody streams={filteredStreams} onStreamChanged={onSingleStreamChanged} />
      </LoadingBackdrop>
    </BulkEditServiceProvider>
  );
};

export const CatalogTree = React.memo(CatalogTreeComponent);
