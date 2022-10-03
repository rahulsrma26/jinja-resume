import os
import asyncio
import pickle
import base64
import shutil
from functools import reduce

import arel
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup

from .utils import read, read_json_files
from .helper import jinja_helpers


SRC_DIR = os.path.dirname(__file__)
APP_DIR = os.path.dirname(SRC_DIR)
STATIC_DIR = os.path.join(APP_DIR, "static")
TEMPLATE_DIR = os.path.join(APP_DIR, "template")
VERSION = read(os.path.join(APP_DIR, "version.txt"))


def reload(app, templates, args=None):
    if not args:
        encoded_args = os.environ.get("JINJA_RESUME_ARGS", None)
        if not encoded_args:
            print("encoded_args not found")
            return app
        args = pickle.loads(base64.b64decode(encoded_args.encode("ascii")))
    app.args = args
    print("ARGS", args)

    async def reload_data():
        app.data = read_json_files(app.args.files)

    if args.reload:
        gen_dirs = [arel.Path(s) for s in [STATIC_DIR, TEMPLATE_DIR]]
        data_files = [arel.Path(s, on_reload=[reload_data]) for s in args.files]
        hot_reload = arel.HotReload(paths=gen_dirs + data_files)
        app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")
        app.add_event_handler("startup", hot_reload.startup)
        app.add_event_handler("startup", reload_data)
        app.add_event_handler("shutdown", hot_reload.shutdown)
        templates.env.globals["BASE_URL"] = ""
        templates.env.globals["DEBUG"] = True
        templates.env.globals["hot_reload"] = hot_reload
        print("embedded Hot-reload using `arel`")
    return app


app = FastAPI()
templates = Jinja2Templates(directory=TEMPLATE_DIR)
templates.env.globals.update(jinja_helpers())
templates.env.globals["BASE_URL"] = "."
app = reload(app, templates)


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        "index.jinja", {"request": request, "VERSION": VERSION, "data": app.data}
    )


app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")


def build(args):
    app.data = read_json_files(args.files)
    if os.path.isdir(args.build_dir):
        print("removing", args.build_dir)
        shutil.rmtree(args.build_dir)
    print("coping", STATIC_DIR, "to", args.build_dir)
    shutil.copytree(STATIC_DIR, args.build_dir)
    print("generating", "index.html")
    with open(os.path.join(args.build_dir, "index.html"), "w", encoding="utf-8") as f:
        soup = BeautifulSoup(root(None).body, "html.parser")
        f.write(soup.prettify())
