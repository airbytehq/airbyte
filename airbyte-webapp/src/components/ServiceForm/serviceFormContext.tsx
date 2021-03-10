import React, { useContext, useMemo } from "react";

import { DropDownRow } from "components";
import { WidgetConfigMap } from "core/form/types";

type Context = {
  formType: "source" | "destination";
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  allowChangeConnector?: boolean;
  onChangeServiceType?: (id: string) => void;
  dropDownData: DropDownRow.IDataItem[];
  documentationUrl?: string;
  widgetsInfo: WidgetConfigMap;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
  unfinishedSecrets: Record<string, { startValue: string }>;
  addUnfinishedSecret: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedSecret: (key: string) => void;
  resetUiFormProgress: () => void;
};

const context: Context = {
  formType: "source",
  dropDownData: [],
  widgetsInfo: {},
  unfinishedSecrets: {},
  setUiWidgetsInfo: (_path: string, _value: Record<string, unknown>) => ({}),
  addUnfinishedSecret: (_key: string, _info?: Record<string, unknown>) => ({}),
  removeUnfinishedSecret: (_key: string) => ({}),
  resetUiFormProgress: () => ({}),
};

const FormWidgetContext = React.createContext<Context>(context);

const useServiceForm = (): Context => useContext(FormWidgetContext);

const ServiceFormContextProvider: React.FC<{
  widgetsInfo: WidgetConfigMap;
  formType: "source" | "destination";
  isLoadingSchema?: boolean;
  isEditMode?: boolean;
  dropDownData: DropDownRow.IDataItem[];
  documentationUrl?: string;
  allowChangeConnector?: boolean;
  onChangeServiceType?: (id: string) => void;
  setUiWidgetsInfo: (path: string, value: Record<string, unknown>) => void;
}> = ({ children, widgetsInfo, setUiWidgetsInfo, ...props }) => {
  const ctx = useMemo<Context>(() => {
    const unfinishedSecrets = widgetsInfo["_common.unfinishedSecrets"] ?? {};
    return {
      widgetsInfo,
      setUiWidgetsInfo,
      formType: props.formType,
      isLoadingSchema: props.isLoadingSchema,
      isEditMode: props.isEditMode,
      onChangeServiceType: props.onChangeServiceType,
      dropDownData: props.dropDownData,
      documentationUrl: props.documentationUrl,
      unfinishedSecrets,
      addUnfinishedSecret: (path, info) =>
        setUiWidgetsInfo("_common.unfinishedSecrets", {
          ...unfinishedSecrets,
          [path]: info ?? {},
        }),
      removeUnfinishedSecret: (path: string) =>
        setUiWidgetsInfo(
          "_common.unfinishedSecrets",
          Object.fromEntries(
            Object.entries(unfinishedSecrets).filter(([key]) => key !== path)
          )
        ),
      resetUiFormProgress: () => {
        setUiWidgetsInfo("_common.unfinishedSecrets", {});
      },
    };
  }, [props, widgetsInfo, setUiWidgetsInfo]);

  return (
    <FormWidgetContext.Provider value={ctx}>
      {children}
    </FormWidgetContext.Provider>
  );
};

const ServiceFormInfo = ({
  children,
}: {
  children: (widgetInfo: Context) => React.ReactElement;
}): React.ReactElement => {
  const widgetInfo = useServiceForm();

  return children(widgetInfo);
};

export { useServiceForm, ServiceFormContextProvider, ServiceFormInfo };
