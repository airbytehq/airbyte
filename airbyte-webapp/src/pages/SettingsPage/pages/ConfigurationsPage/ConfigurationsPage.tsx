import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useAsyncFn } from "react-use";
import styled from "styled-components";

import { Button, ContentCard, Link, LoadingButton } from "components";
import HeadTitle from "components/HeadTitle";

import { useConfig } from "config";
import { DeploymentService } from "core/domain/deployment/DeploymentService";
import { useServicesProvider } from "core/servicesProvider";

import ImportConfigurationModal from "./components/ImportConfigurationModal";
import LogsContent from "./components/LogsContent";

const Content = styled.div`
  max-width: 813px;
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

const ConfigurationsPage: React.FC = () => {
  const config = useConfig();
  const { getService } = useServicesProvider();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const [{ loading }, onImport] = useAsyncFn(
    async (fileBlob: Blob) => {
      try {
        const reader = new FileReader();
        reader.readAsArrayBuffer(fileBlob);

        return new Promise((resolve, reject) => {
          reader.onloadend = async (e) => {
            const file = e?.target?.result;
            if (!file) {
              throw new Error("No file");
            }

            try {
              const deploymentService = getService<DeploymentService>("DeploymentService");
              await deploymentService.importDeployment(new Blob([file]));
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
    },
    [getService]
  );

  const [{ loading: loadingExport }, onExport] = useAsyncFn(async () => {
    const deploymentService = getService<DeploymentService>("DeploymentService");
    const file = await deploymentService.exportDeployment();
    window.location.assign(file);
  }, []);

  return (
    <Content>
      <HeadTitle titles={[{ id: "sidebar.settings" }, { id: "admin.configuration" }]} />
      <ContentCard title={<FormattedMessage id="admin.export" />}>
        <ButtonContent>
          <LoadingButton onClick={onExport} isLoading={loadingExport}>
            <FormattedMessage id="admin.exportConfiguration" />
          </LoadingButton>
          <Text>
            <FormattedMessage
              id="admin.exportConfigurationText"
              values={{
                lnk: (lnk: React.ReactNode) => (
                  <DocLink target="_blank" href={config.links.configurationArchiveLink} as="a">
                    {lnk}
                  </DocLink>
                ),
              }}
            />
          </Text>
        </ButtonContent>
      </ContentCard>

      <ControlContent title={<FormattedMessage id="admin.import" />}>
        <ButtonContent>
          <Button onClick={() => setIsModalOpen(true)}>
            <FormattedMessage id="admin.importConfiguration" />
          </Button>
          <Text>
            <FormattedMessage
              id="admin.importConfigurationText"
              values={{
                warn: (warn: React.ReactNode) => <Warning>{warn}</Warning>,
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

export default ConfigurationsPage;
