from pathlib import Path
from logging.config import dictConfig
from typing import Dict, Optional, Any, List
import json
import pickle
from util.config import Config
from datetime import datetime
import requests
from requests import Response
from pydantic import BaseModel

class Util:
    FORMAT = "[%(levelname)s] %(asctime)s: %(message)s."
    DATE_FORMAT = None

    @staticmethod
    def setup_logging(name, level="INFO", fmt=FORMAT):
        formatted = fmt.format(app=name)
        log_dir = Path(__file__).parent.parent.joinpath("logs")
        log_dir.mkdir(exist_ok=True)

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"standard": {"format": formatted}},
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": level,
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "when": "midnight",
                    "utc": True,
                    "backupCount": 5,
                    "level": level,
                    "filename": "{}/errors.log".format(log_dir),
                    "formatter": "standard",
                },
            },
            "loggers": {
                "": {"handlers": ["default"], "level": level},
                "error_log": {"handlers": ["default", "file"], "level": level},
            },
        }

        dictConfig(logging_config)

    @staticmethod
    def load_json(file: Path):
        with open(file.absolute(), "r+") as f:
            return json.load(f)

    @staticmethod
    def dump_json(file: Path, obj: Dict):
        with open(file.absolute(), "w") as f:
            json.dump(obj, f, indent=4)

    @staticmethod
    def percent_change(value: float, percent: float) -> float:
        return (percent / 100 * value) + value

    @staticmethod
    def load_pickle(file: Path):
        with open(file.absolute(), "rb") as f:
            return pickle.load(f)

    @staticmethod
    def dump_pickle(obj: Any, obj_desc: str, directory: Optional[Path] = None):
        if directory is None:
            file = Config.TEST_DIR.joinpath(
                f'{obj_desc}{datetime.now().strftime("%Y%m%d%H%M%S")}'
            )
        else:
            file = directory.joinpath(f"{obj_desc}{datetime.now().timestamp()}")
        with open(file.absolute(), "wb") as f:
            pickle.dump(obj, f)

    @staticmethod
    def compare_dicts(d1: Dict, d2: Dict, ignore_keys: List[str]) -> bool:
        return {k: v for k, v in d1.items() if k not in ignore_keys} == {
            k: v for k, v in d2.items() if k not in ignore_keys
        }

    @staticmethod
    def post_pipedream(obj: BaseModel) -> Response:
        resp = requests.post(Config.PIPEDREAM_URL, data=obj.json())
        return resp


def convert_ticker(value: str, to_broker: str, pairing: str) -> str:
    if to_broker == "FTX":
        value = value.split(pairing)[0]

        if "PERP" not in value:
            # ETH / USD
            value = value.split("/")[0].strip() + "-PERP"
        return value
    elif to_broker == "Universal":
        value = value.split("USDT")[0]
        return value
    else:
        return value
