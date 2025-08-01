output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "azurerm_search_service_name" {
  value = azurerm_search_service.search.name
}

output "azurerm_search_service_id" {
  value = azurerm_search_service.search.id
}

output "AZURE_STORAGE_CONNECTION_STRING" {
  value     = azurerm_storage_account.drvschstrg.primary_connection_string
  sensitive = true
}

output "AZURE_CONTAINER_NAME" {
  value = azurerm_storage_container.drvschoolcontainer.name
}

output "AZURE_OPENAI_ENDPOINT" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "AZURE_OPENAI_API_KEY" {
  value     = azurerm_cognitive_account.openai.primary_access_key
  sensitive = true
}