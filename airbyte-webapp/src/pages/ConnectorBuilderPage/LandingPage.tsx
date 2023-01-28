import { useFormikContext } from "formik";
import { load, YAMLException } from "js-yaml";
import React, { useCallback, useRef, useState } from "react";
import { FormattedMessage } from "react-intl";

import { BuilderFormValues, DEFAULT_BUILDER_FORM_VALUES } from "components/connectorBuilder/types";
import { useManifestToBuilderForm } from "components/connectorBuilder/useManifestToBuilderForm";
import { Button, ButtonProps } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Heading } from "components/ui/Heading";
import { Text } from "components/ui/Text";
import { ToastType } from "components/ui/Toast";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useNotificationService } from "hooks/services/Notification";
import { useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./LandingPage.module.scss";
import { ReactComponent as AirbyteLogo } from "../../../public/images/airbyte/logo.svg";

const YAML_UPLOAD_ERROR_ID = "connectorBuilder.yamlUpload.error";

export const LandingPage = React.memo(
  ({
    setShowLandingPage,
    switchToUI,
    switchToYaml,
  }: {
    setShowLandingPage: (value: boolean) => void;
    switchToUI: () => void;
    switchToYaml: () => void;
  }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { registerNotification, unregisterNotificationById } = useNotificationService();
    const { setJsonManifest, setYamlIsValid } = useConnectorBuilderFormState();
    const { convertToBuilderFormValues } = useManifestToBuilderForm();
    const { setValues } = useFormikContext<BuilderFormValues>();
    const [importYamlLoading, setImportYamlLoading] = useState(false);

    const handleYamlUpload = useCallback(
      async (yaml: string) => {
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
          setYamlIsValid(true);

          let convertedFormValues;
          try {
            convertedFormValues = await convertToBuilderFormValues(json, DEFAULT_BUILDER_FORM_VALUES);
          } catch (e) {
            switchToYaml();
            setJsonManifest(json);
            setShowLandingPage(false);
            return;
          }

          switchToUI();
          setValues(convertedFormValues);
          setShowLandingPage(false);
        } finally {
          if (fileInputRef.current) {
            fileInputRef.current.value = "";
          }
          setImportYamlLoading(false);
        }
      },
      [
        convertToBuilderFormValues,
        registerNotification,
        setJsonManifest,
        setShowLandingPage,
        setValues,
        setYamlIsValid,
        switchToUI,
        switchToYaml,
      ]
    );

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
        <FlexContainer direction="row">
          <input
            type="file"
            accept=".yml,.yaml"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={(uploadEvent) => {
              setImportYamlLoading(true);
              const file = uploadEvent.target.files?.[0];
              const reader = new FileReader();
              reader.onload = (readerEvent) => {
                handleYamlUpload(readerEvent.target?.result as string);
              };
              if (file) {
                reader.readAsText(file);
              }
            }}
          />
          <Tile
            image={<AirbyteLogo />}
            title="connectorBuilder.landingPage.importYaml.title"
            description="connectorBuilder.landingPage.importYaml.description"
            buttonText="connectorBuilder.landingPage.importYaml.button"
            buttonProps={{ isLoading: importYamlLoading }}
            onClick={() => {
              unregisterNotificationById(YAML_UPLOAD_ERROR_ID);
              fileInputRef.current?.click();
            }}
          />

          <Button
            onClick={() => {
              switchToUI();
              setShowLandingPage(false);
            }}
          >
            Start from scratch
          </Button>
        </FlexContainer>
      </FlexContainer>
    );
  }
);

interface TileProps {
  image: React.ReactNode;
  title: string;
  description: string;
  buttonText: string;
  buttonProps?: Partial<ButtonProps>;
  onClick: () => void;
}

const Tile: React.FC<TileProps> = ({ image, title, description, buttonText, buttonProps, onClick }) => {
  return (
    <FlexContainer direction="column" gap="lg" className={styles.tile}>
      {image}
      <Text>
        <FormattedMessage id={title} />
      </Text>
      <Text>
        <FormattedMessage id={description} />
      </Text>
      <Button onClick={onClick} {...buttonProps}>
        <FormattedMessage id={buttonText} />
      </Button>
    </FlexContainer>
  );
};
