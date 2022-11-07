import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { H5 } from "components/base/Titles";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import { DeleteBlockProps } from "./interfaces";
import { useDeleteModal } from "./useDeleteModal";

const DeleteBlockComponent = styled(Card)`
  margin-top: 12px;
  padding: 19px 20px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Text = styled.div`
  margin-left: 20px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.greyColor40};
  white-space: pre-line;
`;

const DeleteBlock: React.FC<DeleteBlockProps> = ({ type, onDelete }) => {
  const { onDeleteButtonClick } = useDeleteModal({ type, onDelete });

  return (
    <DeleteBlockComponent>
      <Text>
        <H5 bold>
          <FormattedMessage id={`tables.${type}Delete.title`} />
        </H5>
        <FormattedMessage id={`tables.${type}DataDelete`} />
      </Text>
      <Button variant="danger" onClick={onDeleteButtonClick} data-id="open-delete-modal">
        <FormattedMessage id={`tables.${type}Delete`} />
      </Button>
    </DeleteBlockComponent>
  );
};

export default DeleteBlock;
