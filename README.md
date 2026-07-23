# Todo List API

## Project URL

Local API server:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

This API is built around two main resources:

- User
- Todo

### User

A user represents a person who can register, log in, and own todo items.

Fields:

- id
- name
- email
- hashed_password
- created_at

Notes:

- `email` should be unique.
- `hashed_password` stores the protected version of the password, never the plain password.
- A user can own many todos.

### Todo

A todo represents one task created by a user.

Fields:

- id
- title
- description
- completed
- user_id
- created_at
- updated_at

Notes:

- `title` should be required.
- `description` can be optional.
- `completed` should default to false.
- `user_id` connects the todo to the user who owns it.
- `created_at` tracks when the todo was created.
- `updated_at` tracks when the todo was last changed.

### Relationship

The core relationship is:

```text
User has many Todos
Todo belongs to one User
```

That relationship is what makes authentication and authorization meaningful later.
