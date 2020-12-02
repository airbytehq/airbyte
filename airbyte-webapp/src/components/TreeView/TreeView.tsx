import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Button from "../Button";
import TreeViewRow from "./components/TreeViewRow";
import { INode } from "./types";

type IProps = {
  nodes: Array<INode>;
  checked: string[];
  onCheck: (data: string[]) => void;
  checkedAll: string[];
};

const SelectButton = styled(Button)`
  margin: 10px 17px 3px;
  padding: 3px;
  min-width: 90px;
`;

const TreeView: React.FC<IProps> = ({
  nodes,
  checked,
  onCheck,
  checkedAll
}) => {
  // TODO hack for v0.2.0: don't allow checking any of the children aka fields in a stream. This should be removed once it's possible to select
  // these again.
  // https://airbytehq.slack.com/archives/C01CWUQT7UJ/p1603173180066800
  nodes.forEach(n => {
    if (n.children) {
      n.children.forEach(child => (child.hideCheckbox = true));
    }
  });

  const onCheckAll = () => {
    if (checked?.length) {
      onCheck([]);
    } else {
      onCheck(checkedAll);
    }
  };

  return (
    <div>
      <SelectButton onClick={onCheckAll} type="button">
        {checked?.length ? (
          <FormattedMessage id="sources.schemaUnselectAll" />
        ) : (
          <FormattedMessage id="sources.schemaSelectAll" />
        )}
      </SelectButton>
      {nodes.map(item => (
        <TreeViewRow item={item} checked={checked} onCheck={onCheck} />
      ))}
    </div>
  );
};

export default TreeView;
