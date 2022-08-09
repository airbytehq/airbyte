/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { getByTestId, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import selectEvent from "react-select-event";

import { AirbyteJSONSchema } from "core/jsonSchema";
import { render } from "utils/testutils";
import { ServiceForm } from "views/Connector/ServiceForm";

import { DestinationDefinitionSpecificationRead } from "../../../core/request/AirbyteClient";
import { DocumentationPanelContext } from "../ConnectorDocumentationLayout/DocumentationPanelContext";
import { ServiceFormValues } from "./types";

// hack to fix tests. https://github.com/remarkjs/react-markdown/issues/635
jest.mock("components/Markdown", () => ({ children }: React.PropsWithChildren<unknown>) => <>{children}</>);

jest.mock("../ConnectorDocumentationLayout/DocumentationPanelContext", () => {
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  const emptyFn = () => {};

  const useDocumentationPanelContext: () => DocumentationPanelContext = () => ({
    documentationPanelOpen: false,
    documentationUrl: "",
    setDocumentationPanelOpen: emptyFn,
    setDocumentationUrl: emptyFn,
  });

  return {
    useDocumentationPanelContext,
  };
});

jest.setTimeout(10000);

const useAddPriceListItem = (container: HTMLElement) => {
  const priceList = getByTestId(container, "connectionConfiguration.priceList");
  let index = 0;

  return async (name: string, price: string) => {
    const addButton = getByTestId(priceList, "addItemButton");
    await waitFor(() => userEvent.click(addButton));

    const arrayOfObjectsEditModal = getByTestId(document.body, "arrayOfObjects-editModal");
    const getPriceListInput = (index: number, key: string) =>
      arrayOfObjectsEditModal.querySelector(`input[name='__temp__connectionConfiguration_priceList${index}.${key}']`);

    // Type items into input
    const nameInput = getPriceListInput(index, "name");
    userEvent.type(nameInput!, name);

    const priceInput = getPriceListInput(index, "price");
    userEvent.type(priceInput!, price);

    const doneButton = getByTestId(arrayOfObjectsEditModal, "done-button");
    await waitFor(() => userEvent.click(doneButton));

    index++;
  };
};

const schema: AirbyteJSONSchema = {
  type: "object",
  properties: {
    host: {
      type: "string",
      description: "Hostname of the database.",
      title: "Host",
    },
    port: {
      title: "Port",
      type: "integer",
      description: "Port of the database.",
    },
    password: {
      title: "Password",
      airbyte_secret: true,
      type: "string",
      description: "Password associated with the username.",
    },
    credentials: {
      type: "object",
      oneOf: [
        {
          title: "api key",
          properties: {
            api_key: {
              type: "string",
            },
          },
        },
        {
          title: "oauth",
          properties: {
            redirect_uri: {
              type: "string",
              examples: ["https://api.hubspot.com/"],
            },
          },
        },
      ],
    },
    message: {
      type: "string",
      multiline: true,
      title: "Message",
    },
    priceList: {
      type: "array",
      items: {
        type: "object",
        properties: {
          name: {
            type: "string",
            title: "Product name",
          },
          price: {
            type: "integer",
            title: "Price ($)",
          },
        },
      },
    },
    emails: {
      type: "array",
      items: {
        type: "string",
      },
    },
    workTime: {
      type: "array",
      title: "Work time",
      items: {
        type: "string",
        enum: ["day", "night"],
      },
    },
  },
};

jest.mock("hooks/services/Analytics");

jest.mock("hooks/services/useWorkspace", () => ({
  useCurrentWorkspace: () => ({
    workspace: {
      workspaceId: "workspaceId",
    },
  }),
}));

describe("Service Form", () => {
  describe("should display json schema specs", () => {
    let container: HTMLElement;
    beforeEach(async () => {
      const handleSubmit = jest.fn();
      const renderResult = await render(
        <ServiceForm
          formType="source"
          onSubmit={handleSubmit}
          selectedConnectorDefinitionSpecification={
            // @ts-expect-error Partial objects for testing
            {
              connectionSpecification: schema,
              sourceDefinitionId: "1",
              documentationUrl: "",
            } as DestinationDefinitionSpecificationRead
          }
          availableServices={[]}
        />
      );
      container = renderResult.container;
    });

    test("should display general components: submit button, name and serviceType fields", () => {
      const name = container.querySelector("input[name='name']");
      const serviceType = container.querySelector("div[data-testid='serviceType']");
      const submit = container.querySelector("button[type='submit']");

      expect(name).toBeInTheDocument();
      expect(serviceType).toBeInTheDocument();
      expect(submit).toBeInTheDocument();
    });

    test("should display text input field", () => {
      const host = container.querySelector("input[name='connectionConfiguration.host']");
      expect(host).toBeInTheDocument();
      expect(host?.getAttribute("type")).toEqual("text");
    });

    test("should display number input field", () => {
      const port = container.querySelector("input[name='connectionConfiguration.port']");
      expect(port).toBeInTheDocument();
      expect(port?.getAttribute("type")).toEqual("number");
    });

    test("should display secret input field", () => {
      const password = container.querySelector("input[name='connectionConfiguration.password']");
      expect(password).toBeInTheDocument();
      expect(password?.getAttribute("type")).toEqual("password");
    });

    test("should display textarea field", () => {
      const message = container.querySelector("textarea[name='connectionConfiguration.message']");
      expect(message).toBeInTheDocument();
    });

    test("should display oneOf field", () => {
      const credentials = container.querySelector("div[data-testid='connectionConfiguration.credentials']");
      const credentialsValue = credentials?.querySelector("input[value='api key']");
      const apiKey = container.querySelector("input[name='connectionConfiguration.credentials.api_key']");
      expect(credentials).toBeInTheDocument();
      expect(credentials?.getAttribute("role")).toEqual("combobox");
      expect(credentialsValue).toBeInTheDocument();
      expect(apiKey).toBeInTheDocument();
    });

    test("should display array of simple entity field", () => {
      const emails = container.querySelector("input[name='connectionConfiguration.emails']");
      expect(emails).toBeInTheDocument();
    });

    test("should display array with items list field", () => {
      const workTime = container.querySelector("div[name='connectionConfiguration.workTime']");
      expect(workTime).toBeInTheDocument();
    });

    test("should display array of objects field", () => {
      const priceList = container.querySelector("div[data-testid='connectionConfiguration.priceList']");
      const addButton = priceList?.querySelector("button[data-testid='addItemButton']");
      expect(priceList).toBeInTheDocument();
      expect(addButton).toBeInTheDocument();
    });
  });

  describe("filling service form", () => {
    let result: ServiceFormValues;
    let container: HTMLElement;
    beforeEach(async () => {
      const renderResult = await render(
        <ServiceForm
          formType="source"
          formValues={{ name: "test-name", serviceType: "test-service-type" }}
          onSubmit={(values) => (result = values)}
          selectedConnectorDefinitionSpecification={
            // @ts-expect-error Partial objects for testing
            {
              connectionSpecification: schema,
              sourceDefinitionId: "test-service-type",
              documentationUrl: "",
            } as DestinationDefinitionSpecificationRead
          }
          availableServices={[]}
        />
      );
      container = renderResult.container;
    });

    test("should fill all fields by right values", async () => {
      const name = container.querySelector("input[name='name']");
      const host = container.querySelector("input[name='connectionConfiguration.host']");
      const port = container.querySelector("input[name='connectionConfiguration.port']");
      const password = container.querySelector("input[name='connectionConfiguration.password']");
      const message = container.querySelector("textarea[name='connectionConfiguration.message']");
      const apiKey = container.querySelector("input[name='connectionConfiguration.credentials.api_key']");
      const emails = container.querySelector("input[name='connectionConfiguration.emails']");
      const workTime = container.querySelector("div[name='connectionConfiguration.workTime']");

      userEvent.type(name!, "{selectall}{del}name");
      userEvent.type(host!, "test-host");
      userEvent.type(port!, "123");
      userEvent.type(password!, "test-password");
      userEvent.type(message!, "test-message");
      userEvent.type(apiKey!, "test-api-key");
      userEvent.type(emails!, "test@test.com{enter}");
      userEvent.type(workTime!.querySelector("input")!, "day{enter}");

      const addPriceListItem = useAddPriceListItem(container);
      await addPriceListItem("test-price-list-name", "1");

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      expect(result).toEqual({
        name: "name",
        serviceType: "test-service-type",
        connectionConfiguration: {
          credentials: { api_key: "test-api-key" },
          emails: ["test@test.com"],
          host: "test-host",
          message: "test-message",
          password: "test-password",
          port: 123,
          priceList: [{ name: "test-price-list-name", price: 1 }],
          workTime: ["day"],
        },
      });
    });

    test("should fill right values in array of simple entity field", async () => {
      const emails = container.querySelector("input[name='connectionConfiguration.emails']");
      userEvent.type(emails!, "test1@test.com{enter}test2@test.com{enter}test3@test.com");

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      // @ts-expect-error typed unknown, okay in test file
      expect(result.connectionConfiguration.emails).toEqual(["test1@test.com", "test2@test.com", "test3@test.com"]);
    });

    test("should fill right values in array with items list field", async () => {
      const workTime = container.querySelector("div[name='connectionConfiguration.workTime']");
      userEvent.type(workTime!.querySelector("input")!, "day{enter}abc{enter}ni{enter}");

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      // @ts-expect-error typed unknown, okay in test file
      expect(result.connectionConfiguration.workTime).toEqual(["day", "night"]);
    });

    test("change oneOf field value", async () => {
      const credentials = screen.getByTestId("connectionConfiguration.credentials");

      const selectContainer = getByTestId(container, "connectionConfiguration.credentials");

      await selectEvent.select(selectContainer, "oauth", {
        container: document.body,
      });

      const credentialsValue = credentials.querySelector("input[value='oauth']");
      const uri = container.querySelector("input[name='connectionConfiguration.credentials.redirect_uri']");

      expect(credentialsValue).toBeInTheDocument();
      expect(uri).toBeInTheDocument();
    });

    test("should fill right values oneOf field", async () => {
      const selectContainer = getByTestId(container, "connectionConfiguration.credentials");

      await selectEvent.select(selectContainer, "oauth", {
        container: document.body,
      });

      const uri = container.querySelector("input[name='connectionConfiguration.credentials.redirect_uri']");
      userEvent.type(uri!, "test-uri");

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      expect(result.connectionConfiguration).toEqual({
        credentials: { redirect_uri: "test-uri" },
      });
    });

    test("should fill right values in array of objects field", async () => {
      const addPriceListItem = useAddPriceListItem(container);
      await addPriceListItem("test-1", "1");
      await addPriceListItem("test-2", "2");

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      const { connectionConfiguration } = result as {
        connectionConfiguration: { priceList: Array<{ name: string; price: number }> };
      };

      expect(connectionConfiguration.priceList).toEqual([
        { name: "test-1", price: 1 },
        { name: "test-2", price: 2 },
      ]);
    });
  });
});
