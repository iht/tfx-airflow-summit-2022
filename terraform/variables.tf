variable "folder_name" {
  description = "Folder where the project will be hosted. It will be created by TF"
  type = string
}

variable "project_name" {
  description = "The name of the GCP project"
  type = string
}

variable "region" {
  description = "The region for resources and networking"
  type = string
}
variable "organization" {
  description = "Organization for the project/resources"
  type = string
}
variable "billing_account" {
  description = "Billing account for the projects/resources"
  type = string
}
variable "owners" {
  description = "List of owners for the projects and folders"
  type = list(string)
}
variable "quota_project" {
  description = "Quota project used for admin settings"
  type = string
}
