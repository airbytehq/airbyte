#
# Define all the variables that you might want to override
#

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

variable "instance-size" {
  type = string
}

variable "ami-id" {
  type = string
}

variable "key-name" {
  type = string
}

variable "certificate" {
  type = string
}

variable "auth-secret" {
  type = string
}
