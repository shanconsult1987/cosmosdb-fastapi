import os
from dotenv import load_dotenv
from azure.cosmos import CosmosClient
from azure.identity import AzureCliCredential

load_dotenv()

endpoint = os.getenv("COSMOS_ENDPOINT")
db_name = os.getenv("COSMOS_DB_NAME")
container_name = os.getenv("COSMOS_CONTAINER_NAME")

_container = None

def get_container():
	global _container

	if _container is not None:
		return _container

	missing = [
		name
		for name, value in (
			("COSMOS_ENDPOINT", endpoint),
			("COSMOS_DB_NAME", db_name),
			("COSMOS_CONTAINER_NAME", container_name),
		)
		if not value
	]
	if missing:
		raise RuntimeError(f"Missing Cosmos configuration: {', '.join(missing)}")

	try:
		client = CosmosClient(endpoint, credential=AzureCliCredential())
		database = client.get_database_client(db_name)
		_container = database.get_container_client(container_name)
		return _container
	except Exception as exc:
		raise RuntimeError(
			"Cosmos authentication failed with Azure CLI credentials. Run 'az login' and grant that identity Cosmos data-plane RBAC access."
		) from exc