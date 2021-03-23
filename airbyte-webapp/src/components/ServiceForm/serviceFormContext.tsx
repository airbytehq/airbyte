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
  unfinishedFlows: Record<string, { startValue: string; id: number | string }>;
  addUnfinishedFlow: (key: string, info?: Record<string, unknown>) => void;
  removeUnfinishedFlow: (key: string) => void;
  resetUiFormProgress: () => void;
};

const context: Context = {
  formType: "source",
  dropDownData: [],
  widgetsInfo: {},
  setUiWidgetsInfo: (_path: string, _value: Record<string, unknown>) => ({}),
  unfinishedFlows: {},
  addUnfinishedFlow: (_key: string, _info?: Record<string, unknown>) => ({}),
  removeUnfinishedFlow: (_key: string) => ({}),
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
    const unfinishedFlows = widgetsInfo["_common.unfinishedFlows"] ?? {};
    return {
      widgetsInfo,
      setUiWidgetsInfo,
      formType: props.formType,
      isLoadingSchema: props.isLoadingSchema,
      isEditMode: props.isEditMode,
      onChangeServiceType: props.onChangeServiceType,
      dropDownData: props.dropDownData,
      documentationUrl: props.documentationUrl,
      unfinishedFlows: unfinishedFlows,
      addUnfinishedFlow: (path, info) =>
        setUiWidgetsInfo("_common.unfinishedFlows", {
          ...unfinishedFlows,
          [path]: info ?? {},
        }),
      removeUnfinishedFlow: (path: string) =>
        setUiWidgetsInfo(
          "_common.unfinishedFlows",
          Object.fromEntries(
            Object.entries(unfinishedFlows).filter(([key]) => key !== path)
          )
        ),
      resetUiFormProgress: () => {
        setUiWidgetsInfo("_common.unfinishedFlows", {});
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
