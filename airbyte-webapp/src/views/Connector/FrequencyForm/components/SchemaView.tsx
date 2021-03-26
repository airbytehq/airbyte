import React, { useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import TreeView from "components/TreeView";
import { Cell, Header, LightCell } from "components/SimpleTableComponents";
import { SyncSchema } from "core/domain/catalog";
import Search from "./Search";

type IProps = {
  additionalControl?: React.ReactNode;
  schema: SyncSchema;
  onChangeSchema: (schema: SyncSchema) => void;
};

const TreeViewContainer = styled.div`
  width: 100%;
  background: ${({ theme }) => theme.greyColor0};
  margin-bottom: 29px;
  border-radius: 4px;
`;

const SchemaHeader = styled(Header)`
  min-height: 28px;
  margin-bottom: 5px;
`;

const SchemaTitle = styled.div`
  display: inline-block;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  margin: 0 11px 13px 0;
`;

const SchemaView: React.FC<IProps> = ({
  schema,
  onChangeSchema,
  additionalControl,
}) => {
  const hasSelectedItem = useMemo(
    () => schema.streams.some((streamNode) => streamNode.config.selected),
    [schema.streams]
  );

  const onCheckAll = useCallback(() => {
    const allSelectedValues = !hasSelectedItem;

    const newSchema = schema.streams.map((streamNode) => {
      return {
        ...streamNode,
        config: { ...streamNode.config, selected: allSelectedValues },
      };
    });

    onChangeSchema({ streams: newSchema });
  }, [hasSelectedItem, onChangeSchema, schema.streams]);

  const onSearch = useCallback((value: string) => {
    // TODO: add search func
    console.log(value);
    // setCurrentSchema({
    //   streams: schema.streams.filter((stream) =>
    //     stream.stream.name.toLowerCase().includes(value.toLowerCase())
    //   ),
    // });
  }, []);

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
            onSearch={onSearch}
            hasSelectedItem={hasSelectedItem}
          />
        </Cell>
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
        <LightCell>
          <FormattedMessage id="form.syncSettings" />
        </LightCell>
      </SchemaHeader>
      <TreeViewContainer>
        <TreeView schema={schema} onChangeSchema={onChangeSchema} />
      </TreeViewContainer>
    </>
  );
};

export default SchemaView;
