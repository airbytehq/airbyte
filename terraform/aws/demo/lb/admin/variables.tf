variable "name" {
  type = string
}

variable "vpc" {
  type = string
}

variable "default-sg" {
  type = string
}

variable "subnets" {
  type = list(string)
}

variable "instance-id" {
  type = string
}
