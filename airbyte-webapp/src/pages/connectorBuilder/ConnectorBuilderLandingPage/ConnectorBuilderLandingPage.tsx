import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { load, YAMLException } from "js-yaml";
import isEqual from "lodash/isEqual";
import lowerCase from "lodash/lowerCase";
import startCase from "lodash/startCase";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import {
  BuilderFormValues,
  DEFAULT_BUILDER_FORM_VALUES,
  DEFAULT_JSON_MANIFEST_VALUES,
} from "components/connectorBuilder/types";
import { useManifestToBuilderForm } from "components/connectorBuilder/useManifestToBuilderForm";
import { Button, ButtonProps } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";
import { ToastType } from "components/ui/Toast";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useNotificationService } from "hooks/services/Notification";
import {
  ConnectorBuilderLocalStorageProvider,
  useConnectorBuilderLocalStorage,
} from "services/connectorBuilder/ConnectorBuilderLocalStorageService";

import styles from "./ConnectorBuilderLandingPage.module.scss";
import { ReactComponent as AirbyteLogo } from "../../../../public/images/airbyte/logo.svg";
import { ReactComponent as ImportYamlImage } from "../../../../public/images/connector-builder/import-yaml.svg";
import { ReactComponent as StartFromScratchImage } from "../../../../public/images/connector-builder/start-from-scratch.svg";
import { ConnectorBuilderRoutePaths } from "../ConnectorBuilderRoutes";

const YAML_UPLOAD_ERROR_ID = "connectorBuilder.yamlUpload.error";

const ConnectorBuilderLandingPageInner: React.FC = () => {
  const { storedFormValues, setStoredFormValues, storedManifest, setStoredManifest, setStoredEditorView } =
    useConnectorBuilderLocalStorage();
  const navigate = useNavigate();

  // use refs for the intial values because useLocalStorage changes the references on re-render
  const initialStoredFormValues = useRef<BuilderFormValues>(storedFormValues);
  const initialStoredManifest = useRef<ConnectorManifest>(storedManifest);

  useEffect(() => {
    if (
      !isEqual(initialStoredFormValues.current, DEFAULT_BUILDER_FORM_VALUES) ||
      !isEqual(initialStoredManifest.current, DEFAULT_JSON_MANIFEST_VALUES)
    ) {
      navigate(ConnectorBuilderRoutePaths.Edit);
    }
  }, [navigate]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const { registerNotification, unregisterNotificationById } = useNotificationService();
  const { convertToBuilderFormValues } = useManifestToBuilderForm();
  const [importYamlLoading, setImportYamlLoading] = useState(false);

  const handleYamlUpload = useCallback(
    async (uploadEvent: React.ChangeEvent<HTMLInputElement>) => {
      setImportYamlLoading(true);
      const file = uploadEvent.target.files?.[0];
      const reader = new FileReader();
      reader.onload = async (readerEvent) => {
        const yaml = readerEvent.target?.result as string;
        const fileName = file?.name;

        try {
          let json;
          try {
            json = load(yaml) as ConnectorManifest;
          } catch (e) {
            if (e instanceof YAMLException) {
              registerNotification({
                id: YAML_UPLOAD_ERROR_ID,
                text: (
                  <FormattedMessage
                    id={YAML_UPLOAD_ERROR_ID}
                    values={{
                      reason: e.reason,
                      line: e.mark.line,
                    }}
                  />
                ),
                type: ToastType.ERROR,
              });
            }
            return;
          }

          let convertedFormValues;
          try {
            convertedFormValues = await convertToBuilderFormValues(json, DEFAULT_BUILDER_FORM_VALUES);
          } catch (e) {
            setStoredEditorView("yaml");
            setStoredManifest(json);
            navigate(ConnectorBuilderRoutePaths.Edit);
            return;
          }

          if (fileName) {
            const fileNameNoType = lowerCase(fileName.split(".")[0].trim());
            if (fileNameNoType === "manifest") {
              // remove http protocol from beginning of url
              convertedFormValues.global.connectorName = convertedFormValues.global.urlBase.replace(
                /(^\w+:|^)\/\//,
                ""
              );
            } else {
              convertedFormValues.global.connectorName = startCase(fileNameNoType);
            }
          }
          setStoredEditorView("ui");
          setStoredFormValues(convertedFormValues);
          navigate(ConnectorBuilderRoutePaths.Edit);
        } finally {
          if (fileInputRef.current) {
            fileInputRef.current.value = "";
          }
          setImportYamlLoading(false);
        }
      };

      if (file) {
        reader.readAsText(file);
      }
    },
    [
      convertToBuilderFormValues,
      navigate,
      registerNotification,
      setStoredEditorView,
      setStoredFormValues,
      setStoredManifest,
    ]
  );

  // clear out notification on unmount, so it doesn't persist after a redirect
  useEffect(() => {
    return () => unregisterNotificationById(YAML_UPLOAD_ERROR_ID);
  }, [unregisterNotificationById]);

  return (
    <FlexContainer direction="column" alignItems="center" gap="2xl">
      <FlexContainer direction="column" gap="md" alignItems="center" className={styles.titleContainer}>
        <AirbyteLogo />
        <Heading as="h1" size="lg" className={styles.title}>
          <FormattedMessage id="connectorBuilder.landingPage.title" />
        </Heading>
      </FlexContainer>
      <Heading as="h1" size="lg">
        <FormattedMessage id="connectorBuilder.landingPage.prompt" />
      </Heading>
      <FlexContainer direction="row" gap="2xl">
        <input type="file" accept=".yml,.yaml" ref={fileInputRef} onChange={handleYamlUpload} hidden />
        <Tile
          image={<ImportYamlImage />}
          title="connectorBuilder.landingPage.importYaml.title"
          description="connectorBuilder.landingPage.importYaml.description"
          buttonText="connectorBuilder.landingPage.importYaml.button"
          buttonProps={{ isLoading: importYamlLoading }}
          onClick={() => {
            unregisterNotificationById(YAML_UPLOAD_ERROR_ID);
            fileInputRef.current?.click();
          }}
          dataTestId="import-yaml"
        />
        <Tile
          image={<StartFromScratchImage />}
          title="connectorBuilder.landingPage.startFromScratch.title"
          description="connectorBuilder.landingPage.startFromScratch.description"
          buttonText="connectorBuilder.landingPage.startFromScratch.button"
          onClick={() => {
            setStoredEditorView("ui");
            navigate(ConnectorBuilderRoutePaths.Edit);
          }}
          dataTestId="start-from-scratch"
        />
      </FlexContainer>
    </FlexContainer>
  );
};

export const ConnectorBuilderLandingPage: React.FC = () => (
  <ConnectorBuilderLocalStorageProvider>
    <ConnectorBuilderLandingPageInner />
  </ConnectorBuilderLocalStorageProvider>
);

interface TileProps {
  image: React.ReactNode;
  title: string;
  description: string;
  buttonText: string;
  buttonProps?: Partial<ButtonProps>;
  onClick: () => void;
  dataTestId: string;
}

const Tile: React.FC<TileProps> = ({ image, title, description, buttonText, buttonProps, onClick, dataTestId }) => {
  return (
    <Card className={styles.tile}>
      <FlexContainer direction="column" gap="xl" alignItems="center">
        <FlexContainer justifyContent="center" className={styles.tileImage}>
          {image}
        </FlexContainer>
        <FlexContainer direction="column" alignItems="center" gap="md" className={styles.tileText}>
          <Heading as="h2" size="sm" centered>
            <FormattedMessage id={title} />
          </Heading>
          <FlexContainer direction="column" justifyContent="center" className={styles.tileDescription}>
            <Text centered>
              <FormattedMessage id={description} />
            </Text>
          </FlexContainer>
        </FlexContainer>
        <Button onClick={onClick} {...buttonProps} data-testid={dataTestId}>
          <FlexContainer direction="row" alignItems="center" gap="md" className={styles.tileButton}>
            <FontAwesomeIcon icon={faArrowRight} />
            <FormattedMessage id={buttonText} />
          </FlexContainer>
        </Button>
      </FlexContainer>
    </Card>
  );
};
