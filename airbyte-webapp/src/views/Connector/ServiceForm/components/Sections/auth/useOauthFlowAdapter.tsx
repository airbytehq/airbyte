import { setIn, useFormikContext } from "formik";
import get from "lodash/get";
import isEmpty from "lodash/isEmpty";
import merge from "lodash/merge";
import pick from "lodash/pick";
import { useMemo, useState } from "react";

import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { AuthSpecification } from "core/request/AirbyteClient";
import { useRunOauthFlow } from "hooks/services/useConnectorAuth";

import { useServiceForm } from "../../../serviceFormContext";
import { ServiceFormValues } from "../../../types";
import { makeConnectionConfigurationPath, serverProvidedOauthPaths } from "../../../utils";

interface Credentials {
  credentials: AuthSpecification;
}

function useFormikOauthAdapter(connector: ConnectorDefinitionSpecification): {
  loading: boolean;
  done?: boolean;
  hasRun: boolean;
  run: () => Promise<void>;
} {
  const { values, setValues, errors, setFieldTouched } = useFormikContext<ServiceFormValues<Credentials>>();
  const [hasRun, setHasRun] = useState(false);

  const { getValues } = useServiceForm();

  const onDone = (completeOauthResponse: Record<string, unknown>) => {
    let newValues: ServiceFormValues<Credentials>;

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
    setHasRun(true);
  };

  const { run, loading, done } = useRunOauthFlow(connector, onDone);
  const preparedValues = useMemo(() => getValues<Credentials>(values), [getValues, values]);
  const connectionObjectEmpty = preparedValues?.connectionConfiguration?.credentials
    ? Object.keys(preparedValues.connectionConfiguration?.credentials).length <= 1
    : true;

  return {
    loading,
    done: done || !connectionObjectEmpty,
    hasRun,
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

      const oauthInputParams = Object.entries(oauthInputProperties).reduce((acc, property) => {
        acc[property[0]] = get(preparedValues, makeConnectionConfigurationPath(property[1].path_in_connector_config));
        return acc;
      }, {} as Record<string, unknown>);

      await run(oauthInputParams);
    },
  };
}

export { useFormikOauthAdapter };
