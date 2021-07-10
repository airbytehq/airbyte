import React, { useCallback, useMemo, useState } from "react";
import { FieldProps, setIn } from "formik";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import type { DestinationSyncMode } from "core/domain/catalog";
import { SyncSchemaStream } from "core/domain/catalog";

import { CheckBox, LabeledRadioButton } from "components";
import { Header, LightCell } from "components/SimpleTableComponents";
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
  overflow-y: overlay;
`;

const SchemaHeader = styled(Header)`
  min-height: 28px;
  margin-bottom: 5px;
`;

const SchemaTitle = styled(SectionTitle)`
  display: inline-block;
  margin: 0 11px 13px 0;
`;

const SelectAll = styled.div`
  margin: 0 9px 0 30px;
`;

const NamespaceTitleCell = styled(LightCell)`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const SearchContent = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const RadioButtonControl = styled(LabeledRadioButton)`
  margin: 0 0 0 5px;
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
      <SearchContent>
        <Search onSearch={setSearchString} />
        <RadioButtonControl label={<FormattedMessage id="form.all" />} />
        <RadioButtonControl label={<FormattedMessage id="form.selected" />} />
        <RadioButtonControl
          label={<FormattedMessage id="form.notSelected" />}
        />
      </SearchContent>
      <SchemaHeader>
        <NamespaceTitleCell flex={1.5}>
          <SelectAll>
            <CheckBox onChange={onCheckAll} checked={hasSelectedItem} />
          </SelectAll>
          <FormattedMessage id="form.sourceNamespace" />
        </NamespaceTitleCell>
        <LightCell>
          <FormattedMessage id="form.sourceStreamName" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.destinationNamespace" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.destinationStreamName" />
        </LightCell>
        <LightCell flex={1.5}>
          <FormattedMessage id="form.syncMode" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.primaryKey" />
        </LightCell>
        <LightCell>
          <FormattedMessage id="form.cursorField" />
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
