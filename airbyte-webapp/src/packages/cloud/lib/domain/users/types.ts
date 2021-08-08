export interface User {
  email: string;
  name: string;
  userId: string;
  status?: "invited" | "registered" | "disabled";
}
