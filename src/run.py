import os
import pickle
import base64
import uvicorn
import argparse
from .main import build


def file_path(path: str) -> str:
    if os.path.isfile(path):
        return path
    raise ValueError(f"file {path} doesn't exist")


def get_args():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    parser.add_argument("mode", choices=["dev", "build"])
    parser.add_argument(
        "files", type=file_path, nargs="+", help="json files to merge and create data"
    )
    parser.add_argument(
        "-b",
        "--build_dir",
        type=str,
        default="./build",
        help="output directory for build mode",
    )
    parser.add_argument(
        "-r",
        "--reload",
        action="store_const",
        const=True,
        default=False,
        help="start in debug mode",
    )
    return parser.parse_args()


def main(args):
    if args.mode == "dev":
        encoded_args = base64.b64encode(pickle.dumps(args)).decode("ascii")
        os.environ["JINJA_RESUME_ARGS"] = encoded_args
        uvicorn.run("src.main:app", reload=args.reload, log_level="info")
    else:
        build(args)


if __name__ == "__main__":
    main(get_args())
