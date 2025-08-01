output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "azurerm_search_service_name" {
  value = azurerm_search_service.search.name
}

output "azurerm_search_service_id" {
  value = azurerm_search_service.search.id
}