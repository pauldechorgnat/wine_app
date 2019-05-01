from app import create_app, db, cli
from app.models import User, Post, AOC, Cepage, Game

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'AOC': AOC, 'Cepage': Cepage, 'Game': Game}
