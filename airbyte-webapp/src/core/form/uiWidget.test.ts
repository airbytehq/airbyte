import { FormBlock } from "./types";
import { buildPathInitialState } from "./uiWidget";

const formItems: FormBlock[] = [
  {
    _type: "formGroup",
    fieldKey: "key",
    fieldName: "key",
    isRequired: true,
    properties: [
      {
        _type: "formItem",
        fieldKey: "start_date",
        fieldName: "key.start_date",
        isRequired: true,
        type: "string",
      },
      {
        _type: "formCondition",
        fieldKey: "credentials",
        fieldName: "key.credentials",
        isRequired: true,
        conditions: {
          "api key": {
            title: "api key",
            _type: "formGroup",
            fieldKey: "credentials",
            fieldName: "key.credentials",
            isRequired: false,
            properties: [
              {
                _type: "formItem",
                fieldKey: "api_key",
                fieldName: "key.credentials.api_key",
                isRequired: true,
                type: "string",
              },
            ],
          },
          oauth: {
            title: "oauth",
            _type: "formGroup",
            fieldKey: "credentials",
            fieldName: "key.credentials",
            isRequired: false,
            properties: [
              {
                _type: "formItem",
                examples: ["https://api.hubspot.com/"],
                fieldKey: "redirect_uri",
                fieldName: "key.credentials.redirect_uri",
                isRequired: true,
                type: "string",
              },
            ],
          },
        },
      },
    ],
  },
];

test("should select first key by default", () => {
  const uiWidgetState = buildPathInitialState(formItems, {});
  expect(uiWidgetState).toEqual({
    "key.credentials": {
      selectedItem: "api key",
    },
  });
});

test("should select key selected in default values", () => {
  const uiWidgetState = buildPathInitialState(
    formItems,
    {
      key: {
        credentials: {
          redirect_uri: "value",
        },
      },
    },
    {}
  );
  expect(uiWidgetState).toEqual({
    "key.credentials": {
      selectedItem: "oauth",
    },
  });
});
