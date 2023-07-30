# fastapi_backend

## Python Backend Architecture

- `fastapi_backend` runs most of the full feature endpoints and logic in python
- Our core packages & submodule(s):
    - **[py_core](https://github.com/EZCampusDevs/py_core/)** is our core python
      submodule containing primary DB access modules and internal class models.
    - [FastAPI](https://fastapi.tiangolo.com/) is our python backend web framework.
    - [Starlette](https://www.starlette.io/) for security features and which FastAPI is based off
      of.
    - [Pydantic](https://pydantic.dev/) class structures for anything that is endpoint facing.
    - [python-dotenv](https://github.com/theskumar/python-dotenv/) for `.env` variable loading.
    - [SQLAlchemy](https://www.sqlalchemy.org/) for anything SQL.

## File Structure & Conventions

### Pydantic Internal Class Models

- Primary internal classes such as `Course`, `Meeting`, `ExtendedMeeting` are defined within
  the `py_core` submodule.
    - See [github.com/EZCampusDevs/py_core](https://github.com/EZCampusDevs/py_core/).

### Pydantic Request Models

- All pydantic request models are usually found within their endpoint specific modules.
- Request models are named using the following convention:
    - `Request<PascalCaseNameHere>`
    - Example:
      ```python
      from pydantic import BaseModel
      
      class RequestFoo(BaseModel):
        foo_needed_ids: list[int] = []
      ```

### FastAPI Routes & Routers

- All feature endpoint routes and their routers are found in the `/app/routes/` directory.
- Router modules are named using the following convention:
    - `r_<snake_case_name_here>.py`

### FastAPI Endpoint Parameters

- The FastAPI importable default Request model is pulled under the parameter name `r`.
- The endpoint's primary pydantic request model is pulled under the parameter name `r_model`.

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/endpoint-example")
def endpoint_example(r: Request, r_model: RequestFoo):
    pass  # ...
```
