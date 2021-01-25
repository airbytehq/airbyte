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

variable "certificate" {
  type = string
}

variable "instance-id" {
  type = string
}

variable "auth-secret" {
  type = string
}
