import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import { Button } from "components";
import DeleteModal from "./components/DeleteModal";

type IProps = {
  type: "source" | "destination" | "connection";
  onDelete: () => void;
};

const DeleteBlockComponent = styled(ContentCard)`
  margin-top: 12px;
  padding: 29px 28px 27px;
  display: flex;
  align-items: center;
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
        <Button
          danger
          onClick={() => setIsModalOpen(true)}
          data-id="open-delete-modal"
        >
          <FormattedMessage id={`tables.${type}Delete`} />
        </Button>
        <Text>
          <FormattedMessage id={`tables.${type}DataDelete`} />
        </Text>
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
