import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useFetcher } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";
import DeleteModal from "./DeleteModal";
import SourceImplementationResource from "../../../../../core/resources/SourceImplementation";
import useRouter from "../../../../../components/hooks/useRouterHook";
import { Routes } from "../../../../routes";
import ConnectionResource from "../../../../../core/resources/Connection";

type IProps = {
  sourceImplementationId?: string;
  connectionId: string;
  afterDelete: () => void;
};

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

const DeleteSource: React.FC<IProps> = ({
  sourceImplementationId,
  connectionId,
  afterDelete
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { push } = useRouter();

  const sourceImplementationDelete = useFetcher(
    SourceImplementationResource.deleteShape()
  );
  const connectionDelete = useFetcher(ConnectionResource.deleteShape());

  const onDelete = async () => {
    await sourceImplementationDelete({
      sourceImplementationId: sourceImplementationId || ""
    });
    afterDelete();
    push(Routes.Root);

    await connectionDelete({
      connectionId
    });
  };

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
          onSubmit={onDelete}
        />
      )}
    </>
  );
};

export default DeleteSource;
