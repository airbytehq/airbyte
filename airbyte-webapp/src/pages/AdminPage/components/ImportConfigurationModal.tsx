import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Modal from "../../../components/Modal";
import Button from "../../../components/Button";
import FileDropZone from "../../../components/FileDropZone";

export type IProps = {
  onClose: () => void;
  onSubmit: (data: any) => void;
  message?: React.ReactNode;
  isLoading?: boolean;
  error?: any;
  cleanError?: () => void;
};

const Content = styled.div`
  padding: 18px 37px 28px;
  font-size: 14px;
  line-height: 28px;
  width: 485px;
`;
const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;
const DropZoneSubtitle = styled.div`
  font-size: 11px;
  font-weight: bold;
`;
const Bottom = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
  padding-top: 27px;
`;
const Error = styled.div`
  color: ${({ theme }) => theme.dangerColor};
  font-size: 14px;
  line-height: 17px;
  margin-right: 10px;
`;
const Note = styled.div`
  padding-top: 8px;
  text-align: center;
`;

const ImportConfigurationModal: React.FC<IProps> = ({
  onClose,
  onSubmit,
  isLoading,
  error,
  cleanError
}) => {
  const [usersFile, setUsersFile] = useState(null);
  const DropZoneMainText = () => (
    <div>
      <FormattedMessage id="admin.dropZoneTitle" />
      <DropZoneSubtitle>
        <FormattedMessage id="admin.dropZoneSubtitle" />
      </DropZoneSubtitle>
    </div>
  );
  return (
    <Modal
      onClose={onClose}
      title={<FormattedMessage id="admin.importConfiguration" />}
    >
      <Content>
        <FileDropZone
          mainText={<DropZoneMainText />}
          options={{
            onDrop: files => {
              setUsersFile(files[0]);
              if (cleanError) {
                cleanError();
              }
            },
            maxFiles: 1,
            accept:
              "application/x-zip-compressed, application/zip, application/x-gzip, application/x-gtar, application/x-tgz"
          }}
        />
        <Note>
          <FormattedMessage id="admin.reloadAfterSuccess" />
        </Note>
        <Bottom>
          <Error>
            {error ? <FormattedMessage id="form.someError" /> : null}
          </Error>
          <div>
            <ButtonWithMargin onClick={onClose} secondary disabled={isLoading}>
              <FormattedMessage id="form.cancel" />
            </ButtonWithMargin>
            <Button
              onClick={() => onSubmit(usersFile)}
              disabled={!usersFile || isLoading}
            >
              <FormattedMessage id="form.submit" />
            </Button>
          </div>
        </Bottom>
      </Content>
    </Modal>
  );
};

export default ImportConfigurationModal;
