import { prepareMarkdown } from "./DocumentationPanel";

const testMarkdown = `## Some documentation

<!-- ENV:CLOUD -->
### Only relevant for Cloud

some specific documentation that only applies for cloud.
<!-- /ENV:CLOUD -->

<!-- ENV:OSS -->
### Only relevant for OSS users

some specific documentation that only applies for OSS users
<!-- /ENV:OSS -->`;

describe("prepareMarkdown", () => {
  it("should prepare markdown for cloud", () => {
    expect(prepareMarkdown(testMarkdown, "cloud")).toBe(`## Some documentation

<!-- ENV:CLOUD -->
### Only relevant for Cloud

some specific documentation that only applies for cloud.
<!-- /ENV:CLOUD -->

`);
  });
  it("should prepare markdown for oss", () => {
    expect(prepareMarkdown(testMarkdown, "oss")).toBe(`## Some documentation



<!-- ENV:OSS -->
### Only relevant for OSS users

some specific documentation that only applies for OSS users
<!-- /ENV:OSS -->`);
  });
});
