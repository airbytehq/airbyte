// const openReplayConfig: OpenReplayOptions = {
//   projectID:
//     window.OPENREPLAY !== "disabled"
//       ? Number.isInteger(process.env.REACT_APP_OPEN_REPLAY_PROJECT_ID)
//         ? Number.parseInt(process.env.REACT_APP_OPEN_REPLAY_PROJECT_ID ?? "-1")
//         : -1
//       : -1,
//   obscureTextEmails: false,
//   obscureInputEmails: false,
//   revID: Version,
// };
//
// const paperCupsConfig: PaperCupsConfig = {
//   accountId: process.env.REACT_APP_PAPERCUPS_ACCOUNT_ID ?? "",
//   baseUrl: "https://app.papercups.io",
//   enableStorytime:
//     !process.env.REACT_APP_PAPERCUPS_DISABLE_STORYTIME &&
//     window.PAPERCUPS_STORYTIME !== "disabled",
// };
//
// const fullStoryConfig: Fullstory.SnippetOptions = {
//   orgId: process.env.REACT_APP_FULL_STORY_ORG ?? "",
//   devMode: window.FULLSTORY === "disabled",
// };
//
// const config: Config = {
//   ...defaultConfig,
//   segment: {
//     enabled: window.TRACKING_STRATEGY === "segment",
//     token: process.env.REACT_APP_SEGMENT_TOKEN ?? "",
//   },
//   papercups: paperCupsConfig,
//   openreplay: openReplayConfig,
//   fullstory: fullStoryConfig,
//   apiUrl:
//     window.API_URL ||
//     process.env.REACT_APP_API_URL ||
//     `${window.location.protocol}//${window.location.hostname}:8001/api/v1/`,
//   isDemo: window.IS_DEMO === "true",
// };
//

export * from "./defaultConfig";
export * from "./ConfigService";
export * from "./types";
