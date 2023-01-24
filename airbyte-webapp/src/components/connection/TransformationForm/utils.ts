import * as yup from "yup";

export const validationSchema = yup.object({
  name: yup.string().required("form.empty.error"),
  operatorConfiguration: yup.object({
    dbt: yup.object({
      gitRepoUrl: yup
        .string()
        .required("form.empty.error")
        .matches(/((http(s)?)|(git@[\w.]+))(:(\/\/)?)([\w.@:/\-~]+)(\.git)$/, "form.repositoryUrl.invalidUrl"),
      dockerImage: yup.string().required("form.empty.error"),
      dbtArguments: yup.string().required("form.empty.error"),
      gitRepoBranch: yup.string().nullable(),
    }),
  }),
});
