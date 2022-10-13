// import { render } from "@testing-library/react";
import { act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Form, Formik } from "formik";
import selectEvent from "react-select-event";
import mockDest from "test-utils/mock-data/mockDestinationDefinition.json";
import { render, mockConnection } from "test-utils/testutils";
import * as yup from "yup";

import { ScheduleField } from "./ScheduleField";
import { scheduleFieldValidationSchema } from "./validationSchema";

jest.mock("services/connector/DestinationDefinitionSpecificationService", () => ({
  useGetDestinationDefinitionSpecification: () => mockDest,
}));
jest.mock("hooks/services/ConnectionForm/ConnectionFormService", () => ({
  useConnectionFormService: () => ({ mode: "create", connection: mockConnection }),
}));

const MockForm = () => (
  <Formik
    initialValues={{ scheduleData: undefined }}
    validationSchema={yup.object({ scheduleData: scheduleFieldValidationSchema })}
    onSubmit={jest.fn()}
  >
    <Form>
      <ScheduleField />
    </Form>
  </Formik>
);

describe(`${ScheduleField.name}`, () => {
  it("displays a cron expression input", async () => {
    const container = await render(<MockForm />);

    await act(async () => {
      const selectContainer = container.getByTestId("scheduleData");
      await selectEvent.select(selectContainer, "Cron");
    });

    expect(container.getByText(/cron expression\*/i)).toBeInTheDocument();
  });

  it("displays an error message if invalid cron expression is entered", async () => {
    const container = await render(<MockForm />);

    await act(async () => {
      const selectContainer = container.getByTestId("scheduleData");
      await selectEvent.select(selectContainer, "Cron");
      userEvent.type(container.getByTestId("cronExpression"), "{selectall}this is an invalid cron expression");
    });

    const validationMessage = await container.findByText(/invalid cron expression/i);
    expect(validationMessage).toBeInTheDocument();
  });
});
