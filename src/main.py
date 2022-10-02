import os
import json
import shutil

import arel
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup

from .utils import read, merge_dict
from .helper import jinja_helpers


THIS_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(THIS_DIR, "static")
TEMPLATE_DIR = os.path.join(THIS_DIR, "template")
VERSION = read(os.path.join(THIS_DIR, "version.txt"))
DATA_FILE = os.path.join(THIS_DIR, "data.json")
SECRET_FILE = os.path.join(THIS_DIR, "secret.json")
DATA = json.loads(read(DATA_FILE))
if os.path.isfile(SECRET_FILE):
    merge_dict(DATA, json.loads(read(SECRET_FILE)))


app = FastAPI()
templates = Jinja2Templates(directory=TEMPLATE_DIR)
templates.env.globals.update(jinja_helpers())
IS_DEV = bool(os.getenv("DEBUG"))
templates.env.globals["BASE_URL"] = "" if IS_DEV else "."

if IS_DEV:
    hot_reload = arel.HotReload(paths=[arel.Path(THIS_DIR)])
    app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")
    app.add_event_handler("startup", hot_reload.startup)
    app.add_event_handler("shutdown", hot_reload.shutdown)
    templates.env.globals["DEBUG"] = IS_DEV
    templates.env.globals["hot_reload"] = hot_reload


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "index.jinja", {"request": request, "VERSION": VERSION, "data": DATA}
    )


def build(path: str = None):
    if not path:
        path = os.path.join(THIS_DIR, "..", "build")
    print("removing", path)
    shutil.rmtree(path)
    print("coping", STATIC_DIR, "to", path)
    shutil.copytree(STATIC_DIR, path)
    print("generating", "index.html")
    with open(os.path.join(path, "index.html"), "w", encoding="utf-8") as f:
        soup = BeautifulSoup(root(None).body, "html.parser")
        f.write(soup.prettify())


app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    build()
