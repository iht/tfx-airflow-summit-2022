terraform {
 backend "gcs" {
   bucket  = "ihr-tfstate"
   prefix  = "tfx_airflow_summit_2022/state"
 }
}
