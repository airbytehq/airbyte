import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useAsyncFn } from "react-use";

import Button from "components/Button";
import ContentCard from "components/ContentCard";
import config from "config";
import Link from "components/Link";
import ImportConfigurationModal from "./ImportConfigurationModal";
import DeploymentService from "core/resources/DeploymentService";
import LogsContent from "./LogsContent";
import LoadingButton from "components/Button/LoadingButton";

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
  const [error, setError] = useState<Error | null>(null);

  const [{ loading }, onImport] = useAsyncFn(async (fileBlob: Blob) => {
    try {
      const reader = new FileReader();
      reader.readAsArrayBuffer(fileBlob);

      return new Promise((resolve, reject) => {
        reader.onloadend = async (e) => {
          // setError("");
          // setIsLoading(true);
          const file = e?.target?.result;
          if (!file) {
            throw new Error("No file");
          }
          try {
            await DeploymentService.importDeployment(file);

            window.location.reload();
            resolve(true);
          } catch (e) {
            reject(e);
          }
        };
      });
    } catch (e) {
      setError(e);
    }
  });

  const [{ loading: loadingExport }, onExport] = useAsyncFn(async () => {
    const file = await DeploymentService.exportDeployment();
    window.location.assign(file);
  }, []);

  return (
    <Content>
      <ControlContent title={<FormattedMessage id="admin.export" />}>
        <ButtonContent>
          <LoadingButton onClick={onExport} isLoading={loadingExport}>
            <FormattedMessage id="admin.exportConfiguration" />
          </LoadingButton>
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
                ),
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
                b: (...b: React.ReactNode[]) => <Warning>{b}</Warning>,
              }}
            />
          </Text>
          {isModalOpen && (
            <ImportConfigurationModal
              onClose={() => setIsModalOpen(false)}
              onSubmit={onImport}
              isLoading={loading}
              error={error}
              cleanError={() => setError(null)}
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
