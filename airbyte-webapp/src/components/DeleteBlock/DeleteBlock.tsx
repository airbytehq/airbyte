import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import { Button, H5 } from "components";
import DeleteModal from "./components/DeleteModal";

type IProps = {
  type: "source" | "destination" | "connection";
  onDelete: () => Promise<unknown>;
};

const DeleteBlockComponent = styled(ContentCard)`
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

const DeleteBlock: React.FC<IProps> = ({ type, onDelete }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <DeleteBlockComponent>
        <Text>
          <H5 bold>
            <FormattedMessage id={`tables.${type}Delete.title`} />
          </H5>
          <FormattedMessage id={`tables.${type}DataDelete`} />
        </Text>
        <Button
          danger
          onClick={() => setIsModalOpen(true)}
          data-id="open-delete-modal"
        >
          <FormattedMessage id={`tables.${type}Delete`} />
        </Button>
      </DeleteBlockComponent>
      {isModalOpen && (
        <DeleteModal
          type={type}
          onClose={() => setIsModalOpen(false)}
          onSubmit={onDelete}
        />
      )}
    </>
  );
};

export default DeleteBlock;
