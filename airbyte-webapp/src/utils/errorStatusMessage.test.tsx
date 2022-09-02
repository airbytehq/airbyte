import { createFormErrorMessage, FormError } from "./errorStatusMessage";

describe("#errorStatusMessage", () => {
  it("should return a provided error message", () => {
    const errMsg = "test";
    expect(createFormErrorMessage(new Error(errMsg))).toBe(errMsg);
  });

  it("should return null if no error message and no status, or status is 0", () => {
    expect(createFormErrorMessage(new Error())).toBe(null);
    const fakeStatusError = new FormError();
    fakeStatusError.status = 0;
    expect(createFormErrorMessage(fakeStatusError)).toBe(null);
  });

  it("should return a validation error message if status is 400", () => {
    const fakeStatusError = new FormError();
    fakeStatusError.status = 400;
    expect(createFormErrorMessage(fakeStatusError)).toMatchInlineSnapshot(`
      <Memo(MemoizedFormattedMessage)
        id="form.validationError"
      />
    `);
  });

  it("should return a 'some error' message if status is > 0 and not 400", () => {
    const fakeStatusError = new FormError();
    fakeStatusError.status = 401;
    expect(createFormErrorMessage(fakeStatusError)).toMatchInlineSnapshot(`
      <Memo(MemoizedFormattedMessage)
        id="form.someError"
      />
    `);
  });
});
