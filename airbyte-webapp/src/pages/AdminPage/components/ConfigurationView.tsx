import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Button from "../../../components/Button";
import { useFetcher } from "rest-hooks";
import DeploymentResource from "../../../core/resources/Deployment";
import ContentCard from "../../../components/ContentCard";
import config from "../../../config";
import Link from "../../../components/Link";
import ImportConfigurationModal from "./ImportConfigurationModal";
import LogsContent from "./LogsContent";

const Content = styled.div`
  max-width: 813px;
  margin: 4px auto;
`;

const ControlContent = styled(ContentCard)`
  margin-top: 12px;
`;

const ButtonContent = styled.div`
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
  flex: 1 0 0;
`;

const DocLink = styled(Link).attrs({ as: "a" })`
  text-decoration: none;
  display: inline-block;
`;

const Warning = styled.div`
  font-weight: bold;
`;

const ConfigurationView: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const fetchExp = useFetcher(DeploymentResource.exportShape(), true);
  const fetchImp = useFetcher(DeploymentResource.importShape(), true);

  const onExport = async () => {
    const { file } = await fetchExp({});
    window.location.assign(file);
  };

  const onImport = async (file: any) => {
    const reader = new FileReader();
    reader.readAsArrayBuffer(file);

    reader.onload = async e => {
      try {
        setError("");
        setIsLoading(true);
        await fetchImp({}, (e?.target?.result as any) || "");
        window.location.reload();
      } catch (e) {
        setIsLoading(false);
        setError(e);
      }
    };
  };

  return (
    <Content>
      <ControlContent title={<FormattedMessage id="admin.export" />}>
        <ButtonContent>
          <Button onClick={onExport}>
            <FormattedMessage id="admin.exportConfiguration" />
          </Button>
          <Text>
            <FormattedMessage
              id="admin.exportConfigurationText"
              values={{
                lnk: (...lnk: React.ReactNode[]) => (
                  <DocLink
                    target="_blank"
                    href={config.ui.configurationArchiveLink}
                    as="a"
                  >
                    {lnk}
                  </DocLink>
                )
              }}
            />
          </Text>
        </ButtonContent>
      </ControlContent>

      <ControlContent title={<FormattedMessage id="admin.import" />}>
        <ButtonContent>
          <Button onClick={() => setIsModalOpen(true)}>
            <FormattedMessage id="admin.importConfiguration" />
          </Button>
          <Text>
            <FormattedMessage
              id="admin.importConfigurationText"
              values={{
                b: (...b: React.ReactNode[]) => <Warning>{b}</Warning>
              }}
            />
          </Text>
          {isModalOpen && (
            <ImportConfigurationModal
              onClose={() => setIsModalOpen(false)}
              onSubmit={onImport}
              isLoading={isLoading}
              error={error}
              cleanError={() => setError("")}
            />
          )}
        </ButtonContent>
      </ControlContent>

      <ControlContent title={<FormattedMessage id="admin.logs" />}>
        <LogsContent />
      </ControlContent>
    </Content>
  );
};

export default ConfigurationView;
