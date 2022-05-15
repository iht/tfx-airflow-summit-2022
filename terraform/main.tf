// Folder and project
module "tfx_folder" {
  source = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/folder"
  parent = var.organization
  name   = var.folder_name
}

module "tfx_proj" {
  source          = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project"
  billing_account = var.billing_account
  name            = var.project_name
  parent          = module.tfx_folder.id
  services = [
    "bigquery.googleapis.com",
    "dataflow.googleapis.com",
    "aiplatform.googleapis.com",
    "monitoring.googleapis.com",
    "composer.googleapis.com"
  ]
  iam = {
    "roles/composer.ServiceAgentV2Ext" = [
      "serviceAccount:service-${module.tfx_proj.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
    ]
  }

  // Required for Cloud Composer
  oslogin = false
  policy_boolean = {
    "constraints/compute.requireOsLogin" = false
  }
}

// GCS bucket
module "tfx_bucket" {
  source        = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/gcs"
  project_id    = module.tfx_proj.project_id
  name          = module.tfx_proj.project_id
  location      = var.region
  storage_class = "STANDARD"
  force_destroy = true
}

// Service account
module "tfx_sa" {
  source       = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/iam-service-account"
  project_id   = module.tfx_proj.project_id
  name         = "tfx-sa"
  generate_key = false
  iam_project_roles = {
    (module.tfx_proj.project_id) = [
      "roles/logging.logWriter",
      "roles/monitoring.metricWriter",
      "roles/storage.admin",
      "roles/aiplatform.user",
      "roles/bigquery.user",
      "roles/dataflow.admin",
      "roles/dataflow.worker",
      "roles/composer.admin",
      "roles/iam.serviceAccountUser"
    ]
  }
}

// Networking
module "tfx_vpc" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-vpc"
  project_id = module.tfx_proj.project_id
  name       = "default"
  subnets = [{
    ip_cidr_range = "10.1.0.0/24"
    name          = "default"
    region        = var.region
    secondary_ip_range = {
      pods     = "10.16.0.0/14"
      services = "10.20.0.0/24"
    }
  }]
  subnet_private_access = {
    "subnet" = true
  }
}

module "tfx_firewall" {
  source       = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-vpc-firewall"
  project_id   = module.tfx_proj.project_id
  network      = module.tfx_vpc.name
  admin_ranges = [module.tfx_vpc.subnet_ips["${var.region}/default"]]
}

module "tfx_nat" {
  source         = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/net-cloudnat"
  project_id     = module.tfx_proj.project_id
  region         = var.region
  name           = "default"
  router_network = module.tfx_vpc.self_link
}

// Cloud Composer instance
resource "google_composer_environment" "tfx_composer" {
  name    = "tfx-composer"
  region  = var.region
  project = module.tfx_proj.project_id
  depends_on = [
    module.tfx_proj
  ] # for permissions to the Composer service agent
  config {
    software_config {
      image_version = "composer-2-airflow-2"
    }
    node_config {
      network         = module.tfx_vpc.self_link
      subnetwork      = module.tfx_vpc.subnet_self_links["${var.region}/default"]
      service_account = module.tfx_sa.email
      # If cidr blocks are not set now, the ranges will be generated
      # automatically, and TF will fail in subsequent calls to try to update
      # the secondary ranges in the VPC
      ip_allocation_policy {
        services_secondary_range_name = "services"
        cluster_secondary_range_name  = "pods"
      }
    }
    private_environment_config {
      enable_private_endpoint = false
    }
  }
}
