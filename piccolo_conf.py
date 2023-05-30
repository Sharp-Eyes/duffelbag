"""Global configuration for piccolo."""

import os

import dotenv
from piccolo import engine
from piccolo.conf import apps

dotenv.load_dotenv()


DB = engine.PostgresEngine(config={"dsn": os.environ["DB_URI"]})


APP_REGISTRY = apps.AppRegistry(apps=["database.piccolo_app"])
