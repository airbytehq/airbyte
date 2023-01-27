import { useFormikContext } from "formik";
import { load, YAMLException } from "js-yaml";
import React, { useCallback, useRef, useState } from "react";
import { FormattedMessage } from "react-intl";

import { BuilderFormValues, DEFAULT_BUILDER_FORM_VALUES } from "components/connectorBuilder/types";
import { useManifestToBuilderForm } from "components/connectorBuilder/useManifestToBuilderForm";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";
import { ToastType } from "components/ui/Toast";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useNotificationService } from "hooks/services/Notification";
import { useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

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
    const [importLoading, setImportLoading] = useState(false);

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
          setImportLoading(false);
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
      <div>
        <Text>Landing Page</Text>
        <input
          type="file"
          accept=".yml,.yaml"
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={(uploadEvent) => {
            setImportLoading(true);
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
        <Button
          onClick={() => {
            unregisterNotificationById(YAML_UPLOAD_ERROR_ID);
            fileInputRef.current?.click();
          }}
          isLoading={importLoading}
        >
          Import YAML
        </Button>
        <Button
          onClick={() => {
            switchToUI();
            setShowLandingPage(false);
          }}
        >
          Start from scratch
        </Button>
      </div>
    );
  }
);
