resource "azurerm_resource_group" "rg" {
  name     = "az_ai_search_drvsh_rg"
  location = var.resource_group_location
}

resource "azurerm_search_service" "search" {
  name                = "azureaisearchservicedrvschool"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.sku
  replica_count       = var.replica_count
  partition_count     = var.partition_count
}

resource "azurerm_storage_account" "drvschstrg" {
  name                     = "drvschstrg"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" 
  access_tier              = "Hot" 
}

resource "azurerm_storage_container" "drvschoolcontainer" {
  name                  = "drvschoolcontainer"
  storage_account_name  = azurerm_storage_account.drvschstrg.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "drv_blobs" {
  for_each = fileset(path.module, "../smart_driving_school/data/*")

  name                   = trim(each.key, "../smart_driving_school/data/")
  storage_account_name   = azurerm_storage_account.drvschstrg.name
  storage_container_name = azurerm_storage_container.drvschoolcontainer.name
  type                   = "Block"
  source                 = each.key
}



resource "azurerm_cognitive_account" "ca" {
  name                = var.cognitive_account_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = var.cognitive_account_kind
  sku_name            = var.cognitive_account_sku_name
}

resource "azurerm_cognitive_deployment" "cd" {
  name                 = var.cognitive_deployment_name
  cognitive_account_id = azurerm_cognitive_account.ca.id
  model {
    format  = var.cognitive_deployment_model_format
    name    = var.cognitive_deployment_model_name
    version = var.cognitive_deployment_model_version
  }

  sku {
    name = var.cognitive_deployment_sku_name
    capacity = var.cognitive_deployment_sku_capacity
  }
}