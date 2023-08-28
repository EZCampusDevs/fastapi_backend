"""FastAPI main.py module.

Normally to run FastAPI manually using uvicorn you use: "uvicorn main:app --reload" in the terminal
from the directory of this file (main.py). However, here uvicorn is called so FastAPI should run
when main is run.

Remember to get to the docs it looks like this: http://localhost:8000/docs.
"""

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path

    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.realpath(path))


if __name__ == "__main__":
    import app

    sys.exit(app.main())
