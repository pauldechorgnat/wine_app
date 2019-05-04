import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clef_secrete-de-Paul'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    POSTS_PER_PAGE = 25
    GRAPES_PER_PAGE = 10
    AOC_PER_PAGE = 10
    USERS_PER_PAGE = 5

    GAMES_TO_NAMES = dict([('quiz_grape_color', 'Grape Color Quiz'),
                           ('quiz_grape_region', 'Grape Region Quiz'),
                           ('quiz_aoc_color', 'AOC Color Quiz'),
                           ('quiz_aoc_region', 'AOC Region Quiz')])
    NAMES_TO_GAMES = {name: game for game, name in GAMES_TO_NAMES.items()}