import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";
import DeleteModal from "./DeleteModal";

const DeleteBlock = styled(ContentCard)`
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
`;

const DeleteSource: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <DeleteBlock>
        <Button danger onClick={() => setIsModalOpen(true)}>
          <FormattedMessage id="sources.deleteSource" />
        </Button>
        <Text>
          <FormattedMessage id="sources.dataDelete" />
        </Text>
      </DeleteBlock>
      {isModalOpen && (
        <DeleteModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={() => setIsModalOpen(false)}
        />
      )}
    </>
  );
};

export default DeleteSource;
