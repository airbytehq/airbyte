import React from "react";
import InputWithEditButton from "./components/InputWithEditButton";
import { InputProps } from "./types";
import InputView from "./components/InputView";

const Input: React.FC<InputProps> = props =>
  props.withEditButton ? (
    <InputWithEditButton {...props} />
  ) : (
    <InputView {...props} />
  );

export default Input;
