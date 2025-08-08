# Infrastructure Deployment Summary

## Successfully Deployed Resources

- azurerm_cognitive_account.ca
- azurerm_cognitive_deployment.cd
- azurerm_resource_group.rg
- azurerm_search_service.search
- azurerm_storage_account.drvschstrg
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/drinking-and-driving-the-facts.pdf"]
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/driver-Road-Users-Handbook.pdf"]
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/driver-knowledge-test-questions-car.pdf"]
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/driving-road-user-handbook.pdf"]
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/driving-test-preparation.pdf"]
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/guide-to-driving-test.pdf"]
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/hazard-perception-handbook.pdf"]
- azurerm_storage_blob.drv_blobs["../smart_driving_school/data/summary-driving-test-nsw.pdf"]
- azurerm_storage_container.drvschoolcontainer

## Infrastructure Outputs

```
AZURE_CONTAINER_NAME = "drvschoolcontainer"
AZURE_STORAGE_CONNECTION_STRING = <sensitive>
azurerm_search_service_id = "/subscriptions/ID/resourceGroups/az_ai_search_drvsh_rg/providers/Microsoft.Search/searchServices/azureaisearchservicedrvschool"
azurerm_search_service_name = "azureaisearchservicedrvschool"
resource_group_name = "az_ai_search_drvsh_rg"
```

**Total Resources Deployed:** 14
