from fastapi import APIRouter, Depends, Query, Response, status

from app import crud
from app.dependencies import get_current_user
from app.errors import forbidden_error, not_found_error
from app.models import User
from app.schemas import TodoItemCreate, TodoItemListRead, TodoItemRead, TodoItemUpdate

router = APIRouter(prefix="/todos", tags=["todo items"])  # groups todo item/task endpoints under the /todos path and label in the API docs

# Helper used by routes to fetch a todo item/task or return 404 if the ID does not exist.
def _find_todo_item(todo_item_id: int) -> TodoItemRead:
    todo_item = crud.get_todo_item(todo_item_id)

    if todo_item is not None:
        return todo_item

    raise not_found_error("Todo item")


# Helper used by routes to block users from touching todo item/tasks they do not own.
def _require_todo_item_owner(todo_item: TodoItemRead, current_user: User) -> None:
    if todo_item.user_id != current_user.id:
        raise forbidden_error()


# Create a To-Do Item endpoint
@router.post("", response_model=TodoItemRead, status_code=status.HTTP_201_CREATED)
async def create_todo_item(
    todo_item_data: TodoItemCreate,
    current_user: User = Depends(get_current_user),
):
    return crud.create_todo_item(todo_item_data, current_user.id)


# Update a To-Do Item endpoint
@router.put("/{todo_item_id}", response_model=TodoItemRead)
async def update_todo_item(
    todo_item_id: int,
    todo_item_data: TodoItemUpdate,
    current_user: User = Depends(get_current_user),
):
    existing_todo_item = _find_todo_item(todo_item_id)
    _require_todo_item_owner(existing_todo_item, current_user)

    updated_todo_item = crud.update_todo_item(todo_item_id, todo_item_data)

    if updated_todo_item is None:
        raise not_found_error("Todo item")

    return updated_todo_item

# Delete a To-Do Item endpoint
@router.delete("/{todo_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_item(
    todo_item_id: int,
    current_user: User = Depends(get_current_user),
):
    todo_item = _find_todo_item(todo_item_id)
    _require_todo_item_owner(todo_item, current_user)

    was_deleted = crud.delete_todo_item(todo_item_id)

    if not was_deleted:
        raise not_found_error("Todo item")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Get To-Do Items endpoint 1 (GET /todos) i.e., what todo items/tasks exist?
@router.get("", response_model=TodoItemListRead)
async def get_todo_items(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    completed: bool | None = Query(default=None),
    current_user: User = Depends(get_current_user),
):
    items, total = crud.get_todo_items(current_user.id, page, limit, completed)

    return TodoItemListRead(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )

# Get To-Do Items endpoint 2 (GET /todos/{todo_item_id}) i.e., fetch the exact todo item/task
@router.get("/{todo_item_id}", response_model=TodoItemRead)
async def get_todo_item(
    todo_item_id: int,
    current_user: User = Depends(get_current_user),
):
    todo_item = _find_todo_item(todo_item_id)
    _require_todo_item_owner(todo_item, current_user)

    return todo_item
