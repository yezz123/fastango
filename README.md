# Fastapi-lazy 🦥

[![PyPI version](https://badge.fury.io/py/fastapi-lazy.svg)](https://badge.fury.io/py/fastapi-lazy)

Utilities that you use in various projects made in FastAPI.

---

**Source Code**: <https://github.com/yezz123/fastapi-lazy>

**Install the project**: `pip install fastapi-lazy`

---

## Features 🎉

- Use the data contained in the JWT
- Use the username contained in the JWT and fetch data.
- Multi Database Support:
  - Creates the dependency to be used to connect to the Postgresql.
  - Creates the dependency to be used to connect to the MongoDB.
- Support Redis Cache:
  - Creates a `pickle` of the object passed as a parameter and saves it in the Redis which is also passed as a parameter.
  - Read the `pickle` of the object saved in RedisDB and return it as Python object.
- Support UUID generator:
  - Create a custom UUID4 using the current timestamp.

## Development 🚧

You should create a virtual environment and activate it:

```bash
python -m venv venv/
```

```bash
source venv/bin/activate
```

And then install the development dependencies:

```bash
pip install -r requirements.dev.txt
```

### Format the code 💅

Execute the following command to apply `pre-commit` formatting:

```bash
make lint
```

## License 🍻

This project is licensed under the terms of the MIT license.
