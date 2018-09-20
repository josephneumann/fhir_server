# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
import os
from flask_marshmallow import Marshmallow
from flask_principal import Principal
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
ma = Marshmallow()
principal = Principal()
migrate = Migrate()
redis = Redis.from_url(url=os.environ.get('REDIS_URL', 'redis://localhost:6379'))
bcrypt = Bcrypt()
