
resource "azurerm_resource_group" "rg" {
  name     = "az_ai_search_rg"
  location = var.resource_group_location
}

resource "azurerm_search_service" "search" {
  name                = "azaisearchservice"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = var.sku
  replica_count       = var.replica_count
  partition_count     = var.partition_count
}