import React, { useCallback, useMemo, useState } from "react";
import { FieldProps, setIn } from "formik";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import type { DestinationSyncMode } from "core/domain/catalog";
import { SyncSchemaStream } from "core/domain/catalog";

import { Cell, Header, LightCell } from "components/SimpleTableComponents";
import CatalogTree from "./CatalogTree";
import Search from "./Search";
import SectionTitle from "./SectionTitle";
import { naturalComparatorBy } from "utils/objects";

const TreeViewContainer = styled.div`
  width: 100%;
  background: ${({ theme }) => theme.greyColor0};
  margin-bottom: 29px;
  border-radius: 4px;
  max-height: 600px;
  overflow-y: auto;
`;

const SchemaHeader = styled(Header)`
  min-height: 28px;
  margin-bottom: 5px;
`;

const SchemaTitle = styled(SectionTitle)`
  display: inline-block;
  margin: 0 11px 13px 0;
`;

type SchemaViewProps = {
  additionalControl?: React.ReactNode;
  destinationSupportedSyncModes: DestinationSyncMode[];
} & FieldProps<SyncSchemaStream[]>;

const SyncCatalogField: React.FC<SchemaViewProps> = ({
  destinationSupportedSyncModes,
  additionalControl,
  field,
  form,
}) => {
  const { value: streams, name: fieldName } = field;

  const [searchString, setSearchString] = useState("");
  const onChangeSchema = useCallback(
    (newValue: SyncSchemaStream[]) => form.setFieldValue(fieldName, newValue),
    [fieldName, form.setFieldValue]
  );

  const sortedSchema = useMemo(
    () =>
      streams.sort(naturalComparatorBy((syncStream) => syncStream.stream.name)),
    [streams]
  );

  const filteredStreams = useMemo(() => {
    return searchString
      ? sortedSchema.filter((stream) =>
          stream.stream.name.toLowerCase().includes(searchString.toLowerCase())
        )
      : sortedSchema;
  }, [searchString, sortedSchema]);

  const hasSelectedItem = useMemo(
    () => filteredStreams.some((streamNode) => streamNode.config.selected),
    [filteredStreams]
  );

  const onCheckAll = useCallback(() => {
    const allSelectedValues = !hasSelectedItem;

    const newSchema = streams.map((streamNode) => {
      if (
        streamNode.stream.name
          .toLowerCase()
          .includes(searchString.toLowerCase())
      ) {
        return setIn(streamNode, "config.selected", allSelectedValues);
      }

      return streamNode;
    });

    onChangeSchema(newSchema);
  }, [hasSelectedItem, onChangeSchema, streams, searchString]);

  return (
    <>
      <div>
        <SchemaTitle>
          <FormattedMessage id="form.dataSync" />
        </SchemaTitle>
        {additionalControl}
      </div>
      <SchemaHeader>
        <Cell flex={2}>
          <Search
            onCheckAll={onCheckAll}
            onSearch={setSearchString}
            hasSelectedItem={hasSelectedItem}
          />
        </Cell>
        <LightCell>
          <FormattedMessage id="form.namespace" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.dataType" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.cleanedName" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.primaryKey" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.cursorField" />
        </LightCell>
        <LightCell flex={1.5}>
          <FormattedMessage id="form.syncSettings" />
        </LightCell>
      </SchemaHeader>
      <TreeViewContainer>
        <CatalogTree
          streams={filteredStreams}
          onChangeSchema={onChangeSchema}
          destinationSupportedSyncModes={destinationSupportedSyncModes}
        />
      </TreeViewContainer>
    </>
  );
};

export default React.memo(SyncCatalogField);
