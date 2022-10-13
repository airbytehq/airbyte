import { getIn, useFormikContext } from "formik";
import { useCallback, useMemo } from "react";

import { FeatureItem, useFeature } from "hooks/services/Feature";

import { useServiceForm } from "./serviceFormContext";
import { ServiceFormValues } from "./types";
import { makeConnectionConfigurationPath, serverProvidedOauthPaths } from "./utils";

type Path = Array<string | number>;

const withoutOneOfPaths = (paths: Path): string[] => {
  return paths.filter((p): p is string => typeof p !== "number" && !/^\d+$/.test(p));
};

const createPathFromAuthSpecification = (paths?: Path[], rootPath: Path = []): string[] => {
  return (
    paths?.map((pathParts) => {
      return makeConnectionConfigurationPath([...withoutOneOfPaths(rootPath ?? []), ...withoutOneOfPaths(pathParts)]);
    }) ?? []
  );
};

interface AuthenticationHook {
  /**
   *
   */
  isFieldImplicitAuthField: (fieldPath: string) => boolean;
  authErrors: Record<string, string>;
  isAuthFlowSelected: boolean;
  oAuthButtonPath: string;
}

export const useAuthentication = (): AuthenticationHook => {
  const { values, getFieldMeta, submitCount } = useFormikContext<ServiceFormValues>();
  const { selectedConnector, getValues } = useServiceForm();

  const allowOAuthConnector = useFeature(FeatureItem.AllowOAuthConnector);

  const advancedAuth = selectedConnector?.advancedAuth;
  const legacyOauthSpec = selectedConnector?.authSpecification?.oauth2Specification;

  const isAuthFlowSelected = useMemo(
    () =>
      Boolean(
        allowOAuthConnector &&
          ((selectedConnector?.authSpecification?.oauth2Specification && !selectedConnector.advancedAuth) ||
            (selectedConnector?.advancedAuth &&
              selectedConnector?.advancedAuth.predicateValue ===
                getIn(
                  getValues(values),
                  makeConnectionConfigurationPath(selectedConnector?.advancedAuth.predicateKey ?? [])
                )))
      ),
    [selectedConnector, allowOAuthConnector, values, getValues]
  );

  // Fields that are filled by the OAuth flow and thus should be hidden from the UI
  const implicitAuthFieldPaths = useMemo(
    () => [
      // Fields from `advancedAuth` connectors
      ...(advancedAuth
        ? Object.values(serverProvidedOauthPaths(selectedConnector)).map((f) =>
            makeConnectionConfigurationPath(f.path_in_connector_config)
          )
        : []),
      // Fields from legacy `authSpecification` connectors
      ...(legacyOauthSpec
        ? [
            ...createPathFromAuthSpecification(
              legacyOauthSpec.oauthFlowInitParameters,
              legacyOauthSpec.rootObject as Path
            ),
            ...createPathFromAuthSpecification(
              legacyOauthSpec.oauthFlowOutputParameters,
              legacyOauthSpec.rootObject as Path
            ),
          ]
        : []),
    ],
    [advancedAuth, legacyOauthSpec, selectedConnector]
  );

  const isFieldImplicitAuthField = useCallback(
    (fieldPath: string) => {
      return implicitAuthFieldPaths.includes(fieldPath);
    },
    [implicitAuthFieldPaths]
  );

  const authErrors = useMemo(() => {
    return implicitAuthFieldPaths.reduce<Record<string, string>>((authErrors, fieldName) => {
      const { error } = getFieldMeta(fieldName);
      if (submitCount > 0 && error) {
        authErrors[fieldName] = error;
      }
      return authErrors;
    }, {});
  }, [getFieldMeta, implicitAuthFieldPaths, submitCount]);

  const oAuthButtonPath = advancedAuth
    ? advancedAuth.predicateKey && makeConnectionConfigurationPath(advancedAuth.predicateKey)
    : legacyOauthSpec && makeConnectionConfigurationPath(withoutOneOfPaths(legacyOauthSpec.rootObject as Path));

  console.log("legacyAuth", legacyOauthSpec);
  console.log("implicitFields", implicitAuthFieldPaths);
  console.log("oAuthButtonPath", oAuthButtonPath);

  return {
    isFieldImplicitAuthField,
    authErrors,
    isAuthFlowSelected,
    oAuthButtonPath: oAuthButtonPath ?? "connectionConfiguration",
  };
};
