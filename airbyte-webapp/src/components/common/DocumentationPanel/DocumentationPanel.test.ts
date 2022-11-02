import { prepareMarkdown } from "./DocumentationPanel";

const testMarkdown = `## Some documentation

<!-- env:cloud -->
### Only relevant for Cloud

some specific documentation that only applies for cloud.
<!-- /env:cloud -->

<!-- env:oss -->
### Only relevant for OSS users

some specific documentation that only applies for OSS users
<!-- /env:oss -->`;

describe("prepareMarkdown", () => {
  it("should prepare markdown for cloud", () => {
    expect(prepareMarkdown(testMarkdown, "cloud")).toBe(`## Some documentation

<!-- env:cloud -->
### Only relevant for Cloud

some specific documentation that only applies for cloud.
<!-- /env:cloud -->

`);
  });
  it("should prepare markdown for oss", () => {
    expect(prepareMarkdown(testMarkdown, "oss")).toBe(`## Some documentation



<!-- env:oss -->
### Only relevant for OSS users

some specific documentation that only applies for OSS users
<!-- /env:oss -->`);
  });
});
