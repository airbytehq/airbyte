export enum CloudRoutes {
  Root = "/",
  AuthFlow = "/auth_flow",

  Metrics = "metrics",
  SelectWorkspace = "workspaces",
  Credits = "credits",

  // Auth routes
  Signup = "/signup",
  Login = "/login",
  ResetPassword = "/reset-password",

  // Firebase action routes
  // These URLs come from Firebase emails, and all have the same
  // action URL ("/verify-email") with different "mode" parameter
  // TODO: use a better action URL in Firebase email template
  FirebaseAction = "/verify-email",
}
