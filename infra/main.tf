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
