interface ErrorMessage {
  code: number;
  message: string;
  zhMessage: string;
}

const errorMsgs: ErrorMessage[] = [
  { code: 200, message: "Success", zhMessage: "成功" },
  { code: 401, message: "Invalid login information", zhMessage: "登录信息无效" },
  { code: 402, message: "User has logged in elsewhere", zhMessage: "用户已在别处登录" },
  { code: 403, message: "Insufficient permissions", zhMessage: "权限不足" },
  { code: 404, message: "Resource not found", zhMessage: "找不到相关资源" },
  { code: 405, message: "Wrong request mode", zhMessage: "请求方式错误" },
  { code: 406, message: "Error requesting Content-Type", zhMessage: "请求内容类型时出错" },
  { code: 407, message: "Lack of parameter", zhMessage: "缺少参数" },
  { code: 408, message: "Parameter format error", zhMessage: "参数格式错误" },
  { code: 409, message: "Parameter type error", zhMessage: "参数类型错误" },
  { code: 411, message: "Error: Parameter body is empty", zhMessage: "参数约束错误" },
  { code: 412, message: "Invalid verification code", zhMessage: "错误：参数体为空" },
  { code: 422, message: "Parameter constraint error", zhMessage: "验证码无效" },
  { code: 500, message: "Server is busy. Please try again later", zhMessage: "服务器繁忙，请稍后再试" },
  { code: 503, message: "Server is busy. Please try again later", zhMessage: "服务器繁忙，请稍后再试" },
  { code: 600, message: "Email already exists", zhMessage: "邮箱已经存在" },
  { code: 601, message: "Incorrect email or password", zhMessage: "邮箱或密码不正确" },
  { code: 602, message: "Passwords do not match. Please try again", zhMessage: "密码不匹配，请重试" },
  { code: 603, message: "Email sending failed", zhMessage: "邮件发送失败" },
  { code: 604, message: "The user is registered", zhMessage: "用户已注册" },
  { code: 605, message: "Google authentication failed", zhMessage: "谷歌认证失败" },
  {
    code: 606,
    message: "The authorization email address and the invitation email address are inconsistent",
    zhMessage: "授权邮箱与邀请邮箱不一致",
  },
  { code: 607, message: "User is invited to activate without registration", zhMessage: "邀请用户在未注册的情况下激活" },
  { code: 701, message: "Confirm the upgrade information first", zhMessage: "先确认升级信息" },
  { code: 702, message: "Status error", zhMessage: "状态错误" },
  { code: 703, message: "Please select upgrade product item", zhMessage: "请选择升级项目" },
  { code: 704, message: "Non-administrator user", zhMessage: "非管理员用户" },
  { code: 705, message: "Expiration of free trial", zhMessage: "免费试用期已过" },
  { code: 706, message: "Value already exists", zhMessage: "值已经存在" },
  { code: 707, message: "Expiration of subscription", zhMessage: "订阅到期" },
  { code: 708, message: "Use over limit", zhMessage: "使用超出限制" },
];

const getErrorMessageByCode = (code: number): string => {
  const errorMsg = errorMsgs.find((msg) => msg.code === code);
  return errorMsg ? errorMsg.message : "";
};

export { getErrorMessageByCode };
