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
 * them as well as prefix them with the `connectionConfiguration` prefix that Formik uses for all connector
 * parameter values, and joins them to string paths.
 */
const convertAndPrefixPaths = (paths?: Path[], rootPath: Path = []): string[] => {
  return (
    paths?.map((pathParts) => {
      return makeConnectionConfigurationPath([...stripNumericalEntries(rootPath), ...stripNumericalEntries(pathParts)]);
    }) ?? []
  );
};

/**
 * Returns true if the auth button should be shown for an advancedAuth specification.
 * This will check if the connector has a predicateKey, and if so, check if the current form value
 * of the corresponding field matches the predicateValue from the specification.
 */
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

/**
 * Returns true if the auth button should be shown for an authSpecification connector.
 */
const shouldShowButtonForLegacyAuth = (
  spec: JSONSchema7,
  rootPath: Path,
  values: ServiceFormValues<unknown>
): boolean => {
  if (!rootPath.some((p) => isNumerical(p))) {
    // If the root path of the auth parameters (which is also the place the button will be rendered)
    // is not inside a conditional, i.e. none of the root path is a numerical value, we will always
    // show the button.
    return true;
  }

  // If the spec had a root path inside a conditional, e.g. `credentials.0`, we need to figure
  // out if that conditional is currently on the correct selected option. Unlike `advancedAuth`
  // which has a `predicateValue`, the legacy auth configuration doesn't have the value for the conditional,
  // so we need to find that ourselves first.

  // To find the path inside the connector spec that matches the `rootPath` we'll need to insert `properties`
  // and `oneOf`, since they'll appear in the JSONSchema, e.g. this turns `credentials.0` to `properties.credentials.oneOf.0`
  const specPath = rootPath.flatMap((path) =>
    isNumerical(path) ? ["oneOf", String(path)] : ["properties", String(path)]
  );
  // Get the part of the spec that `rootPath` point to
  const credentialsSpecRoot = getIn(spec, specPath) as JSONSchema7 | undefined;

  if (!credentialsSpecRoot?.properties) {
    // if the path doesn't exist in the spec (which should not happen) we just show the auth button always.
    return true;
  }

  // To find the value we're expecting, we run through all properties inside that matching spec inside the conditional
  // to find the one that has a `const` value in it, since this is the actual value that will be written into the conditional
  // field itself once it's selected.
  const constProperty = Object.entries(credentialsSpecRoot.properties)
    .map(([key, prop]) => [key, typeof prop !== "boolean" ? prop.const : undefined] as const)
    .find(([, constValue]) => !!constValue);

  // If none of the conditional properties is a const value, we'll also show the auth button always (should not happen)
  if (!constProperty) {
    return true;
  }

  // Check if the value in the form matches the found `const` value from the spec. If so we know the conditional
  // is on the right option.
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
  /**
   * A record of all formik errors in hidden authentication fields. The key will be the
   * name of the field and the value an error code. If no error is present in a field
   * it will be missing from this object.
   */
  hiddenAuthFieldErrors: Record<string, string>;
  /**
   * This will return true if the auth button should be visible and rendered in the place of
   * the passed in field, and false otherwise.
   */
  shouldShowAuthButton: (fieldPath: string) => boolean;
  /**
   * This will return true if any of the hidden auth fields have values.  This determines
   * whether we will render "authenticate" or "re-authenticate" on the OAuth button text
   */
  hasAuthFieldValues: boolean;
}

export const useAuthentication = (): AuthenticationHook => {
  const { values, getFieldMeta, submitCount } = useFormikContext<ServiceFormValues>();
  const { selectedConnector } = useServiceForm();

  const allowOAuthConnector = useFeature(FeatureItem.AllowOAuthConnector);

  const advancedAuth = selectedConnector?.advancedAuth;
  const legacyOauthSpec = selectedConnector?.authSpecification?.oauth2Specification;

  const spec = selectedConnector?.connectionSpecification as JSONSchema7;

  const isAuthButtonVisible = useMemo(() => {
    const shouldShowAdvancedAuth =
      advancedAuth && shouldShowButtonForAdvancedAuth(advancedAuth.predicateKey, advancedAuth.predicateValue, values);
    const shouldShowLegacyAuth =
      legacyOauthSpec && shouldShowButtonForLegacyAuth(spec, legacyOauthSpec.rootObject as Path, values);
    return Boolean(allowOAuthConnector && (shouldShowAdvancedAuth || shouldShowLegacyAuth));
  }, [values, advancedAuth, legacyOauthSpec, spec, allowOAuthConnector]);

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
    if (!isAuthButtonVisible) {
      // We don't want to return the errors if the auth button isn't visible.
      return {};
    }
    return implicitAuthFieldPaths.reduce<Record<string, string>>((authErrors, fieldName) => {
      const { error } = getFieldMeta(fieldName);
      if (submitCount > 0 && error) {
        authErrors[fieldName] = error;
      }
      return authErrors;
    }, {});
  }, [getFieldMeta, implicitAuthFieldPaths, isAuthButtonVisible, submitCount]);

  const shouldShowAuthButton = useCallback(
    (fieldPath: string) => {
      if (!isAuthButtonVisible) {
        // Never show the auth button anywhere if its not enabled or visible (inside a conditional that's not selected)
        return false;
      }

      const path = advancedAuth
        ? advancedAuth.predicateKey && makeConnectionConfigurationPath(advancedAuth.predicateKey)
        : legacyOauthSpec && makeConnectionConfigurationPath(stripNumericalEntries(legacyOauthSpec.rootObject as Path));

      return fieldPath === (path ?? makeConnectionConfigurationPath());
    },
    [advancedAuth, isAuthButtonVisible, legacyOauthSpec]
  );

  const hasAuthFieldValues: boolean = useMemo(() => {
    return implicitAuthFieldPaths.some((path) => getIn(values, path) !== undefined);
  }, [implicitAuthFieldPaths, values]);

  return {
    isHiddenAuthField,
    hiddenAuthFieldErrors,
    shouldShowAuthButton,
    hasAuthFieldValues,
  };
};
