import userEvent from "@testing-library/user-event";
import { findByText, screen, waitFor } from "@testing-library/react";

import ServiceForm from "views/Connector/ServiceForm";
import { render } from "utils/testutils";
import { ServiceFormValues } from "./types";
import { AirbyteJSONSchema } from "core/jsonSchema";

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

describe("Service Form", () => {
  describe("should display json schema specs", () => {
    let container: HTMLElement;
    beforeEach(() => {
      const handleSubmit = jest.fn();
      const renderResult = render(
        <ServiceForm
          formType="source"
          onSubmit={handleSubmit}
          specifications={schema}
          availableServices={[]}
        />
      );
      container = renderResult.container;
    });

    test("should display general components: submit button, name and serviceType fields", () => {
      const name = container.querySelector("input[name='name']");
      const serviceType = container.querySelector(
        "div[data-testid='serviceType']"
      );
      const submit = container.querySelector("button[type='submit']");

      expect(name).toBeInTheDocument();
      expect(serviceType).toBeInTheDocument();
      expect(submit).toBeInTheDocument();
    });

    test("should display text input field", () => {
      const host = container.querySelector(
        "input[name='connectionConfiguration.host']"
      );
      expect(host).toBeInTheDocument();
      expect(host?.getAttribute("type")).toEqual("text");
    });

    test("should display number input field", () => {
      const port = container.querySelector(
        "input[name='connectionConfiguration.port']"
      );
      expect(port).toBeInTheDocument();
      expect(port?.getAttribute("type")).toEqual("number");
    });

    test("should display secret input field", () => {
      const password = container.querySelector(
        "input[name='connectionConfiguration.password']"
      );
      expect(password).toBeInTheDocument();
      expect(password?.getAttribute("type")).toEqual("password");
    });

    test("should display textarea field", () => {
      const message = container.querySelector(
        "textarea[name='connectionConfiguration.message']"
      );
      expect(message).toBeInTheDocument();
    });

    test("should display oneOf field", () => {
      const credentials = container.querySelector(
        "div[data-testid='connectionConfiguration.credentials']"
      );
      const credentialsValue = credentials?.querySelector(
        "input[value='api key']"
      );
      const apiKey = container.querySelector(
        "input[name='connectionConfiguration.credentials.api_key']"
      );
      expect(credentials).toBeInTheDocument();
      expect(credentials?.getAttribute("role")).toEqual("combobox");
      expect(credentialsValue).toBeInTheDocument();
      expect(apiKey).toBeInTheDocument();
    });

    test("should display array of simple entity field", () => {
      const emails = container.querySelector(
        "input[name='connectionConfiguration.emails']"
      );
      expect(emails).toBeInTheDocument();
    });

    test("should display array with items list field", () => {
      const workTime = container.querySelector(
        "div[name='connectionConfiguration.workTime']"
      );
      expect(workTime).toBeInTheDocument();
    });

    test("should display array of objects field", () => {
      const priceList = container.querySelector(
        "div[data-testid='connectionConfiguration.priceList']"
      );
      const addButton = priceList?.querySelector(
        "button[data-testid='addItemButton']"
      );
      expect(priceList).toBeInTheDocument();
      expect(addButton).toBeInTheDocument();
    });
  });

  describe("filling service form", () => {
    let result: ServiceFormValues;
    let container: HTMLElement;
    beforeEach(() => {
      const renderResult = render(
        <ServiceForm
          formType="source"
          formValues={{ name: "test-name", serviceType: "test-service-type" }}
          onSubmit={(values) => (result = values)}
          specifications={schema}
          availableServices={[]}
        />
      );
      container = renderResult.container;
    });

    test("should fill all fields by right values", async () => {
      const name = container.querySelector("input[name='name']");
      const host = container.querySelector(
        "input[name='connectionConfiguration.host']"
      );
      const port = container.querySelector(
        "input[name='connectionConfiguration.port']"
      );
      const password = container.querySelector(
        "input[name='connectionConfiguration.password']"
      );
      const message = container.querySelector(
        "textarea[name='connectionConfiguration.message']"
      );
      const apiKey = container.querySelector(
        "input[name='connectionConfiguration.credentials.api_key']"
      );
      const emails = container.querySelector(
        "input[name='connectionConfiguration.emails']"
      );
      const workTime = container.querySelector(
        "div[name='connectionConfiguration.workTime']"
      );
      const priceList = container.querySelector(
        "div[data-testid='connectionConfiguration.priceList']"
      );
      const addButton = priceList?.querySelector(
        "button[data-testid='addItemButton']"
      );

      userEvent.type(name!, "{selectall}{del}name");
      userEvent.type(host!, "test-host");
      userEvent.type(port!, "123");
      userEvent.type(password!, "test-password");
      userEvent.type(message!, "test-message");
      userEvent.type(apiKey!, "test-api-key");
      userEvent.type(emails!, "test@test.com{enter}");
      userEvent.type(workTime!.querySelector("input")!, "day{enter}");

      await waitFor(() => userEvent.click(addButton!));
      const listName = container.querySelector(
        "input[name='connectionConfiguration.priceList.0.name']"
      );
      const listPrice = container.querySelector(
        "input[name='connectionConfiguration.priceList.0.price']"
      );
      const done = priceList?.querySelector(
        "button[data-testid='done-button']"
      );
      userEvent.type(listName!, "test-price-list-name");
      userEvent.type(listPrice!, "1");
      await waitFor(() => userEvent.click(done!));

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
      const emails = container.querySelector(
        "input[name='connectionConfiguration.emails']"
      );
      userEvent.type(
        emails!,
        "test1@test.com{enter}test2@test.com{enter}test3@test.com"
      );

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      expect(result.connectionConfiguration.emails).toEqual([
        "test1@test.com",
        "test2@test.com",
        "test3@test.com",
      ]);
    });

    test("should fill right values in array with items list field", async () => {
      const workTime = container.querySelector(
        "div[name='connectionConfiguration.workTime']"
      );
      userEvent.type(
        workTime!.querySelector("input")!,
        "day{enter}abc{enter}ni{enter}"
      );

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      expect(result.connectionConfiguration.workTime).toEqual(["day", "night"]);
    });

    test.skip("change oneOf field value", async () => {
      const credentials = screen.getByTestId(
        "connectionConfiguration.credentials"
      );

      userEvent.click(credentials);

      const oauth = await findByText(credentials, "oauth");

      userEvent.click(oauth);

      const credentialsValue = credentials.querySelector(
        "input[value='oauth']"
      );

      const uri = container.querySelector(
        "input[name='connectionConfiguration.credentials.redirect_uri']"
      );

      expect(credentialsValue).toBeInTheDocument();
      expect(uri).toBeInTheDocument();
    });

    test.skip("should fill right values oneOf field", async () => {
      const credentials = screen.getByTestId(
        "connectionConfiguration.credentials"
      );

      userEvent.click(credentials);

      const oauth = await findByText(credentials, "oauth");

      userEvent.click(oauth);

      const uri = container.querySelector(
        "input[name='connectionConfiguration.credentials.redirect_uri']"
      );
      userEvent.type(uri!, "test-uri");

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      expect(result.connectionConfiguration).toEqual({
        credentials: { redirect_uri: "test-uri" },
      });
    });

    test("should fill right values in array of objects field", async () => {
      const priceList = container.querySelector(
        "div[data-testid='connectionConfiguration.priceList']"
      );
      let addButton = priceList?.querySelector(
        "button[data-testid='addItemButton']"
      );
      await waitFor(() => userEvent.click(addButton!));

      const done = priceList!.querySelector(
        "button[data-testid='done-button']"
      );

      const name1 = container.querySelector(
        "input[name='connectionConfiguration.priceList.0.name']"
      );
      const price1 = container.querySelector(
        "input[name='connectionConfiguration.priceList.0.price']"
      );
      userEvent.type(name1!, "test-1");
      userEvent.type(price1!, "1");
      await waitFor(() => userEvent.click(done!));
      addButton = priceList?.querySelector(
        "button[data-testid='addItemButton']"
      );
      await waitFor(() => userEvent.click(addButton!));

      const name2 = container.querySelector(
        "input[name='connectionConfiguration.priceList.1.name']"
      );
      const price2 = container.querySelector(
        "input[name='connectionConfiguration.priceList.1.price']"
      );

      userEvent.type(name2!, "test-2");
      userEvent.type(price2!, "2");
      await waitFor(() => userEvent.click(done!));

      const submit = container.querySelector("button[type='submit']");
      await waitFor(() => userEvent.click(submit!));

      expect(result.connectionConfiguration.priceList).toEqual([
        { name: "test-1", price: 1 },
        { name: "test-2", price: 2 },
      ]);
    });
  });
});
