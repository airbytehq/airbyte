import { getIn, useFormikContext } from "formik";
import { JSONSchema7 } from "json-schema";
import { useCallback, useMemo } from "react";

import { FeatureItem, useFeature } from "hooks/services/Feature";

import { useServiceForm } from "./serviceFormContext";
import { ServiceFormValues } from "./types";
import { makeConnectionConfigurationPath, serverProvidedOauthPaths } from "./utils";

type Path = Array<string | number>;

const isNumerical = (input: string | number): boolean => {
  return typeof input === "number" || /^\d+$/.test(input);
};

/**
 * Takes an array of strings or numbers and remove all elements from it that are either
 * a number or a string that just contains a number. This will be used to remove index
 * accessors into oneOf from paths, since they are not part of the field path later.
 */
const stripNumericalEntries = (paths: Path): string[] => {
  return paths.filter((p): p is string => !isNumerical(p));
};

/**
 * Takes a list of paths in an array representation as well as a root path in array representation, concats
 * them as well as prefix them with the `configurationConfiguration` prefix that Formik uses for all connector
 * parameter values, and joins them to string paths.
 */
const convertAndPrefixPaths = (paths?: Path[], rootPath: Path = []): string[] => {
  return (
    paths?.map((pathParts) => {
      return makeConnectionConfigurationPath([...stripNumericalEntries(rootPath), ...stripNumericalEntries(pathParts)]);
    }) ?? []
  );
};

const shouldShowButtonForAdvancedAuth = (
  predicateKey: string[] | undefined,
  predicateValue: string | undefined,
  values: ServiceFormValues<unknown>
): boolean => {
  return (
    !predicateKey ||
    predicateKey.length === 0 ||
    predicateValue === getIn(values, makeConnectionConfigurationPath(predicateKey))
  );
};

const shouldShowButtonForLegacyAuth = (
  spec: JSONSchema7,
  rootPath: Path,
  values: ServiceFormValues<unknown>
): boolean => {
  if (!rootPath.some((p) => isNumerical(p))) {
    return true;
  }

  const specPath = (rootPath as string[]).flatMap((path) =>
    isNumerical(path) ? ["oneOf", path] : ["properties", path]
  );
  const credentialsSpecRoot = getIn(spec, specPath) as JSONSchema7 | undefined;

  if (!credentialsSpecRoot?.properties) {
    return true;
  }

  const constProperty = Object.entries(credentialsSpecRoot.properties)
    .map(([key, prop]) => [key, typeof prop !== "boolean" ? prop.const : undefined] as const)
    .find(([, constValue]) => !!constValue);

  if (!constProperty) {
    return true;
  }

  const [key, constValue] = constProperty;
  const value = getIn(values, makeConnectionConfigurationPath(stripNumericalEntries([...rootPath, key])));
  return value === constValue;
};

interface AuthenticationHook {
  /**
   * Returns whether a given field path should be hidden, because it's part of the
   * OAuth flow and will be filled in by that.
   */
  isHiddenAuthField: (fieldPath: string) => boolean;
  hiddenAuthFieldErrors: Record<string, string>;
  shouldShowAuthButton: (fieldPath: string) => boolean;
}

export const useAuthentication = (): AuthenticationHook => {
  const { values, getFieldMeta, submitCount } = useFormikContext<ServiceFormValues>();
  const { selectedConnector, getValues } = useServiceForm();

  const allowOAuthConnector = useFeature(FeatureItem.AllowOAuthConnector);

  const advancedAuth = selectedConnector?.advancedAuth;
  const legacyOauthSpec = selectedConnector?.authSpecification?.oauth2Specification;

  const spec = selectedConnector?.connectionSpecification as JSONSchema7;

  const isAuthButtonVisible = useMemo(() => {
    const vals = getValues(values);
    const shouldShowAdvancedAuth =
      advancedAuth && shouldShowButtonForAdvancedAuth(advancedAuth.predicateKey, advancedAuth.predicateValue, vals);
    const shouldShowLegacyAuth =
      legacyOauthSpec && shouldShowButtonForLegacyAuth(spec, legacyOauthSpec.rootObject as Path, vals);
    return Boolean(allowOAuthConnector && (shouldShowAdvancedAuth || shouldShowLegacyAuth));
  }, [getValues, values, advancedAuth, legacyOauthSpec, spec, allowOAuthConnector]);

  // Fields that are filled by the OAuth flow and thus won't need to be shown in the UI if OAuth is available
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
            ...convertAndPrefixPaths(legacyOauthSpec.oauthFlowInitParameters, legacyOauthSpec.rootObject as Path),
            ...convertAndPrefixPaths(legacyOauthSpec.oauthFlowOutputParameters, legacyOauthSpec.rootObject as Path),
          ]
        : []),
    ],
    [advancedAuth, legacyOauthSpec, selectedConnector]
  );

  const isHiddenAuthField = useCallback(
    (fieldPath: string) => {
      // A field should be hidden due to OAuth if we have OAuth enabled and selected (in case it's inside a oneOf)
      // and the field is part of the OAuth flow parameters.
      return isAuthButtonVisible && implicitAuthFieldPaths.includes(fieldPath);
    },
    [implicitAuthFieldPaths, isAuthButtonVisible]
  );

  const hiddenAuthFieldErrors = useMemo(() => {
    return implicitAuthFieldPaths.reduce<Record<string, string>>((authErrors, fieldName) => {
      const { error } = getFieldMeta(fieldName);
      if (submitCount > 0 && error) {
        authErrors[fieldName] = error;
      }
      return authErrors;
    }, {});
  }, [getFieldMeta, implicitAuthFieldPaths, submitCount]);

  const shouldShowAuthButton = useCallback(
    (fieldPath: string) => {
      if (!isAuthButtonVisible) {
        // Never show the auth button anywhere if its not enabled or visible
        return false;
      }

      const path = advancedAuth
        ? advancedAuth.predicateKey && makeConnectionConfigurationPath(advancedAuth.predicateKey)
        : legacyOauthSpec && makeConnectionConfigurationPath(stripNumericalEntries(legacyOauthSpec.rootObject as Path));

      return fieldPath === (path ?? makeConnectionConfigurationPath());
    },
    [advancedAuth, isAuthButtonVisible, legacyOauthSpec]
  );

  return {
    isHiddenAuthField,
    hiddenAuthFieldErrors,
    shouldShowAuthButton,
  };
};
