import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncMode,
  SyncSchema,
  SyncSchemaStream,
} from "core/domain/catalog";
import * as yup from "yup";

type ConnectionFormValues = {
  frequency: string;
  prefix: string;
  schema: SyncSchema;
};

const connectionValidationSchema = yup.object<ConnectionFormValues>({
  frequency: yup.string().required("form.empty.error"),
  prefix: yup.string(),
  schema: yup.object<SyncSchema>({
    streams: yup.array().of(
      yup.object<SyncSchemaStream>({
        id: yup
          .string()
          // This is required to get rid of id fields we are using to detect stream for edition
          .when("$isRequest", (isRequest: boolean, schema: yup.StringSchema) =>
            isRequest ? schema.strip(true) : schema
          ),
        stream: yup.object(),
        // @ts-ignore
        config: yup.object().test({
          name: "connectionSchema.config.validator",
          // eslint-disable-next-line no-template-curly-in-string
          message: "${path} is wrong",
          test: function (value: AirbyteStreamConfiguration) {
            if (!value.selected) {
              return true;
            }
            if (DestinationSyncMode.Dedupted === value.destinationSyncMode) {
              if (value.primaryKey.length === 0) {
                return this.createError({
                  message: "connectionForm.primaryKey.required",
                  path: `schema.streams[${this.parent.id}].config.primaryKey`,
                });
              }
            }

            if (SyncMode.Incremental === value.syncMode) {
              if (
                !this.parent.stream.sourceDefinedCursor &&
                value.cursorField.length === 0
              ) {
                return this.createError({
                  message: "connectionForm.cursorField.required",
                  path: `schema.streams[${this.parent.id}].config.cursorField`,
                });
              }
            }
            return true;
          },
        }),
      })
    ),
  }),
});

const SUPPORTED_MODES: [SyncMode, DestinationSyncMode][] = [
  [SyncMode.FullRefresh, DestinationSyncMode.Overwrite],
  [SyncMode.FullRefresh, DestinationSyncMode.Append],
  [SyncMode.Incremental, DestinationSyncMode.Append],
  [SyncMode.Incremental, DestinationSyncMode.Dedupted],
];

export type { ConnectionFormValues };
export { connectionValidationSchema, SUPPORTED_MODES };
