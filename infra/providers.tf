terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.1"
    }
  }

  # backend "azurerm" {
  #   resource_group_name   = "azureworkshop-demo-rg"
  #   storage_account_name  = "azureworkshopdemostorage"
  #   container_name        = "tfstateopenai"
  #   key                   = "terraform.tfstate"
  # }
}

provider "azurerm" {
  features {}

  subscription_id = "0c2f3539-4920-4f54-9bdb-edf032b716a2"
}
#Azure subscription 1    Default Directory