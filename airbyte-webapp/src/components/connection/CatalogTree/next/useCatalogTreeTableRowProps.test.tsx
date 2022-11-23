/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { renderHook } from "@testing-library/react-hooks";
import classNames from "classnames";
import * as formik from "formik";

import { AirbyteStreamAndConfiguration } from "core/request/AirbyteClient";
import * as bulkEditService from "hooks/services/BulkEdit/BulkEditService";
import * as connectionFormService from "hooks/services/ConnectionForm/ConnectionFormService";
import { FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

// eslint-disable-next-line css-modules/no-unused-class
import styles from "./CatalogTreeTableRow.module.scss";
import { useCatalogTreeTableRowProps } from "./useCatalogTreeTableRowProps";

const mockStream: Partial<AirbyteStreamAndConfiguration> = {
  stream: {
    name: "stream_name",
    namespace: "stream_namespace",
  },
  config: { selected: true, syncMode: "full_refresh", destinationSyncMode: "overwrite" },
};

const mockInitialValues: Partial<FormikConnectionFormValues> = {
  syncCatalog: {
    streams: [
      {
        stream: {
          name: "stream_name",
          namespace: "stream_namespace",
        },
        config: { selected: true, syncMode: "full_refresh", destinationSyncMode: "overwrite" },
      },
    ],
  },
};

const mockDisabledInitialValues: Partial<FormikConnectionFormValues> = {
  syncCatalog: {
    streams: [
      {
        ...mockInitialValues.syncCatalog?.streams[0],
        config: { ...mockInitialValues.syncCatalog!.streams[0].config!, selected: false },
      },
    ],
  },
};

const testSetup = (initialValues: Partial<FormikConnectionFormValues>, isBulkEdit: boolean, error: unknown) => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [isBulkEdit, () => null] as any); // not selected for bulk edit
  jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
    // eslint-disable-next-line
    return { initialValues: initialValues } as any;
  });
  jest.spyOn(formik, "useField").mockImplementationOnce(() => {
    // eslint-disable-next-line
    return [{}, { error: error }] as any; // no error
  });
};

describe("useCatalogTreeTableRowProps", () => {
  it("should return default styles for a row that starts enabled", () => {
    testSetup(mockInitialValues, false, undefined);

    const { result } = renderHook(() => useCatalogTreeTableRowProps(mockStream));

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent));
    expect(result.current.pillButtonVariant).toEqual("grey");
  });
  it("should return disabled styles for a row that starts disabled", () => {
    testSetup(mockDisabledInitialValues, false, undefined);

    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, selected: false },
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.disabled));
    expect(result.current.pillButtonVariant).toEqual("grey");
  });
  it("should return added styles for a row that is added", () => {
    testSetup(mockDisabledInitialValues, false, undefined);

    const { result } = renderHook(() => useCatalogTreeTableRowProps(mockStream));

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.added));
    expect(result.current.pillButtonVariant).toEqual("green");
  });
  it("should return removed styles for a row that is removed", () => {
    testSetup(mockInitialValues, false, undefined);

    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, selected: false },
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.removed));
    expect(result.current.pillButtonVariant).toEqual("red");
  });
  it("should return updated styles for a row that is updated", () => {
    // eslint-disable-next-line
    testSetup(mockInitialValues, false, undefined);

    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, syncMode: "incremental", destinationSyncMode: "append_dedup" },
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.changed));
    expect(result.current.pillButtonVariant).toEqual("blue");
  });

  it("should return added styles for a row that is both added and updated", () => {
    testSetup(mockDisabledInitialValues, false, undefined);

    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { selected: true, syncMode: "incremental", destinationSyncMode: "append_dedup" }, // selected true, new sync, mode and destination sync mode
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.added));
    expect(result.current.pillButtonVariant).toEqual("green");
  });
  it("should return change background color if selected for bulk edit", () => {
    testSetup(mockInitialValues, true, undefined);

    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, selected: true }, // selected true, new sync, mode and destination sync mode
      })
    );
    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.changed));
    expect(result.current.pillButtonVariant).toEqual("blue");
  });
  it("should return error styles for a row that has an error", () => {
    testSetup(mockInitialValues, false, "error");

    const { result } = renderHook(() => useCatalogTreeTableRowProps(mockStream));

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.error));
  });
});
