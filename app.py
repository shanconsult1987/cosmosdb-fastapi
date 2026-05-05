from fastapi import FastAPI, HTTPException
from cosmos import get_container
import uuid

app = FastAPI()


def require_container():
    try:
        return get_container()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

# Create User
@app.post("/users")
def create_user(name: str, age: int):
    container = require_container()
    user = {
        "id": str(uuid.uuid4()),
        "userId": name,   # partition key
        "name": name,
        "age": age
    }
    container.create_item(user)
    return user


# Get User
@app.get("/users/{user_id}")
def get_user(user_id: str):
    container = require_container()
    try:
        item = container.read_item(item=user_id, partition_key=user_id)
        return item
    except:
        raise HTTPException(status_code=404, detail="User not found")


# Query Users
@app.get("/users")
def list_users():
    container = require_container()
    query = "SELECT * FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    return items


# Update User
@app.put("/users/{user_id}")
def update_user(user_id: str, age: int):
    container = require_container()
    item = container.read_item(item=user_id, partition_key=user_id)
    item["age"] = age
    container.replace_item(item, item)
    return item


# Delete User
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    container = require_container()
    container.delete_item(item=user_id, partition_key=user_id)
    return {"message": "Deleted"}

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",        # file_name:fastapi_instance
        host="127.0.0.1",
        port=8000,
        reload=True       # auto-reload on changes
    )