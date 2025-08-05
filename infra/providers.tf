terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.1"
    }
  }
}

provider "azurerm" {
  features {}

  subscription_id = "0c2f3539-4920-4f54-9bdb-edf032b716a2"
}
