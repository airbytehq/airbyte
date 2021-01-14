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
};

const Content = styled.div`
  padding: 18px 37px 28px;
  font-size: 14px;
  line-height: 28px;
  width: 485px;
`;
const ButtonContent = styled.div`
  padding-top: 27px;
  text-align: right;
`;
const ButtonWithMargin = styled(Button)`
  margin-right: 9px;
`;
const DropZoneSubtitle = styled.div`
  font-size: 11px;
  font-weight: bold;
`;

const ImportConfigurationModal: React.FC<IProps> = ({ onClose, onSubmit }) => {
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
            onDrop: files => setUsersFile(files[0]),
            maxFiles: 1,
            accept: "application/x-gzip, application/x-gtar, application/x-tgz"
          }}
        />
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} secondary>
            <FormattedMessage id="form.cancel" />
          </ButtonWithMargin>
          <Button onClick={() => onSubmit(usersFile)} disabled={!usersFile}>
            <FormattedMessage id="form.submit" />
          </Button>
        </ButtonContent>
      </Content>
    </Modal>
  );
};

export default ImportConfigurationModal;
