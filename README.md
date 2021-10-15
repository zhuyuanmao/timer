# a timer django backend. 

## How to run the server.

1. Run the command on project root directory.
```
docker-compose up --build
```
2. Access the server via `localhost:8000`.

## API Specs.

#### Get a list of tasks.
```http
GET  /tasks
```
Request body: `None`

Response Body: 
```json
[
    {
        "id": "df5a297e-ee77-4d43-bbe5-b04aaa91ee1d",
        "name": "study",
        "status": 2,
        "duration": 10,
        "remainder": 10,
        "start_at": null,
        "end_at": null
    }
]

```
#### Get a task
```http
GET  /tasks/:task_id
```
Request body: `None`

Response Body: 
```json
{
    "id": "df5a297e-ee77-4d43-bbe5-b04aaa91ee1d",
    "name": "study",
    "status": 2,
    "duration": 10,
    "remainder": 10,
    "start_at": null,
    "end_at": null
}

```
#### Create a task
```http
GET  /tasks
```
Request body: 
```json
{
    "name": "study",
    "duration": 10,
    "webhook_url": "http://example.webhook.com"
}
```

Response Body: 
```json
{
    "id": "df5a297e-ee77-4d43-bbe5-b04aaa91ee1d",
    "name": "study",
    "status": 2,
    "duration": 10,
    "remainder": 10,
    "start_at": null,
    "end_at": null
}

```

#### Operate a task
```http
GET  /tasks/:task_id/operations
```
Request body: (`start`, `resume`, `pause`)
```json
{
    "operation": "resume"
}
```

Response Body: 
```json
{
    "id": "df5a297e-ee77-4d43-bbe5-b04aaa91ee1d",
    "name": "study",
    "status": 2,
    "duration": 10,
    "remainder": 10,
    "start_at": null,
    "end_at": null
}

```
