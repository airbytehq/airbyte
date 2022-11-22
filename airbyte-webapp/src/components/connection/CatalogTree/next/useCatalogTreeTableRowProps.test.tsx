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

describe("<CatalogTreeTableRow />", () => {
  it("should return default styles for a row that starts enabled", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [false, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      // eslint-disable-next-line
      return { initialValues: mockInitialValues } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });

    const { result } = renderHook(() => useCatalogTreeTableRowProps(mockStream));

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent));
    expect(result.current.statusIcon).toEqual(null);
    expect(result.current.pillButtonVariant).toEqual("grey");
  });
  it("should return disabled styles for a row that starts disabled", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [false, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      return {
        initialValues: {
          syncCatalog: {
            streams: [
              {
                ...mockInitialValues.syncCatalog?.streams[0],
                config: { ...mockInitialValues.syncCatalog?.streams[0].config, selected: false },
              },
            ],
          },
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });
    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, selected: false },
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.disabled));
    expect(result.current.statusIcon).toEqual(null);
    expect(result.current.pillButtonVariant).toEqual("grey");
  });
  it("should return added styles for a row that is added", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [false, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      return {
        initialValues: {
          syncCatalog: {
            streams: [
              {
                ...mockInitialValues.syncCatalog?.streams[0],
                config: { ...mockInitialValues.syncCatalog?.streams[0].config, selected: false },
              },
            ],
          },
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });
    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, selected: true }, // selected true
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.added));
    // we care that iconName="plus" and className="icon plus" but it is tricky to test a react node returned from a hook like this
    expect(result.current.statusIcon).toMatchSnapshot();
    expect(result.current.pillButtonVariant).toEqual("green");
  });
  it("should return removed styles for a row that is removed", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [false, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      return {
        initialValues: { ...mockInitialValues },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });
    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, selected: false }, // selected false
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.removed));

    // we care that iconName="minus" and className="icon minus" but it is tricky to test a react node returned from a hook like this
    expect(result.current.statusIcon).toMatchSnapshot();
    expect(result.current.pillButtonVariant).toEqual("red");
  });
  it("should return updated styles for a row that is updated", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [false, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      return {
        initialValues: { ...mockInitialValues },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });
    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, syncMode: "incremental", destinationSyncMode: "append_dedup" }, // new sync mode and destination sync mode
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.changed));
    // we care that this is our custom ModificationIcon component with modificationColor as its color
    expect(result.current.statusIcon).toMatchSnapshot();
    expect(result.current.pillButtonVariant).toEqual("blue");
  });
  it("should return added styles for a row that is both added and updated", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [false, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      return {
        initialValues: {
          syncCatalog: {
            streams: [
              {
                ...mockInitialValues.syncCatalog?.streams[0],
                config: { ...mockInitialValues.syncCatalog?.streams[0].config, selected: false },
              },
            ],
          },
        }, // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });
    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { selected: true, syncMode: "incremental", destinationSyncMode: "append_dedup" }, // selected true, new sync, mode and destination sync mode
      })
    );

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.added));
    // we care that iconName="plus" and className="icon plus" but it is tricky to test a react node returned from a hook like this
    expect(result.current.statusIcon).toMatchSnapshot();
    expect(result.current.pillButtonVariant).toEqual("green");
  });
  it("should return change background color with relevant icon if selected for bulk edit", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [true, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      return {
        initialValues: {
          syncCatalog: {
            streams: [
              {
                ...mockInitialValues.syncCatalog?.streams[0],
                config: { ...mockInitialValues.syncCatalog?.streams[0].config, selected: false },
              },
            ],
          },
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any;
    });

    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });

    const { result } = renderHook(() =>
      useCatalogTreeTableRowProps({
        ...mockStream,
        config: { ...mockStream.config!, selected: true }, // selected true, new sync, mode and destination sync mode
      })
    );
    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.changed));
    // we care that iconName="plus" and className="icon plus" but it is tricky to test a react node returned from a hook like this
    expect(result.current.statusIcon).toMatchSnapshot();
    expect(result.current.pillButtonVariant).toEqual("blue");
  });
  it("should return change background color and override icon color with relevant icon if selected for bulk edit", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [true, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      // eslint-disable-next-line
      return { initialValues: mockInitialValues } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: undefined }] as any; // no error
    });

    const { result } = renderHook(() => useCatalogTreeTableRowProps(mockStream));

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.changed));
    // we care that iconName="plus" and className="icon plus" but it is tricky to test a react node returned from a hook like this
    expect(result.current.statusIcon).toMatchSnapshot();
    expect(result.current.pillButtonVariant).toEqual("blue");
  });
  it("should return error styles for a row that has an error", () => {
    // eslint-disable-next-line
    jest.spyOn(bulkEditService, "useBulkEditSelect").mockImplementation(() => [false, () => null] as any); // not selected for bulk edit
    jest.spyOn(connectionFormService, "useConnectionFormService").mockImplementation(() => {
      // eslint-disable-next-line
      return { initialValues: mockInitialValues } as any;
    });
    jest.spyOn(formik, "useField").mockImplementationOnce(() => {
      // eslint-disable-next-line
      return [{}, { error: true }] as any; // no error
    });

    const { result } = renderHook(() => useCatalogTreeTableRowProps(mockStream));

    expect(result.current.streamHeaderContentStyle).toEqual(classNames(styles.streamHeaderContent, styles.error));
  });
});
