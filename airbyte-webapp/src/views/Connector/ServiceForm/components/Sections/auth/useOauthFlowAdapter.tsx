import { setIn, useFormikContext } from "formik";
import get from "lodash/get";
import isEmpty from "lodash/isEmpty";
import merge from "lodash/merge";
import pick from "lodash/pick";

import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { useRunOauthFlow } from "hooks/services/useConnectorAuth";

import { useServiceForm } from "../../../serviceFormContext";
import { ServiceFormValues } from "../../../types";
import { makeConnectionConfigurationPath, serverProvidedOauthPaths } from "../../../utils";

function useFormikOauthAdapter(connector: ConnectorDefinitionSpecification): {
  loading: boolean;
  done?: boolean;
  run: () => Promise<void>;
} {
  const { values, setValues, errors, setFieldTouched } = useFormikContext<ServiceFormValues>();

  const { getValues } = useServiceForm();

  const onDone = (completeOauthResponse: Record<string, unknown>) => {
    let newValues: ServiceFormValues;

    if (connector.advancedAuth) {
      const oauthPaths = serverProvidedOauthPaths(connector);

      newValues = Object.entries(oauthPaths).reduce(
        (acc, [key, { path_in_connector_config }]) =>
          setIn(acc, makeConnectionConfigurationPath(path_in_connector_config), completeOauthResponse[key]),
        values
      );
    } else {
      newValues = merge(values, {
        connectionConfiguration: completeOauthResponse,
      });
    }

    setValues(newValues);
  };

  const { run, loading, done } = useRunOauthFlow(connector, onDone);

  return {
    loading,
    done,
    run: async () => {
      const oauthInputProperties =
        (
          connector?.advancedAuth?.oauthConfigSpecification?.oauthUserInputFromConnectorConfigSpecification as {
            properties: Array<{ path_in_connector_config: string[] }>;
          }
        )?.properties ?? {};

      if (!isEmpty(oauthInputProperties)) {
        const oauthInputFields =
          Object.values(oauthInputProperties)?.map((property) =>
            makeConnectionConfigurationPath(property.path_in_connector_config)
          ) ?? [];

        oauthInputFields.forEach((path) => setFieldTouched(path, true, true));

        const oAuthErrors = pick(errors, oauthInputFields);

        if (!isEmpty(oAuthErrors)) {
          return;
        }
      }

      const preparedValues = getValues(values);

      const oauthInputParams = Object.entries(oauthInputProperties).reduce((acc, property) => {
        acc[property[0]] = get(preparedValues, makeConnectionConfigurationPath(property[1].path_in_connector_config));
        return acc;
      }, {} as Record<string, unknown>);

      await run(oauthInputParams);
    },
  };
}

export { useFormikOauthAdapter };
