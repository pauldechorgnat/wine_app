from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user_):
        if not self.is_following(user_):
            self.followed.append(user_)

    def unfollow(self, user_):
        if self.is_following(user_):
            self.followed.remove(user_)

    def is_following(self, user_):
        return self.followed.filter(
            followers.c.followed_id == user_.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Grape(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    regions = db.Column(db.String(140))
    vineyards = db.Column(db.String(140))
    departments = db.Column(db.String(140))
    area_fr = db.Column(db.Integer)
    area_world = db.Column(db.Integer)
    red = db.Column(db.Boolean, index=True)


class AOC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    vineyard = db.Column(db.String(140))
    still_white_wine = db.Column(db.Boolean)
    still_rose_wine = db.Column(db.Boolean)
    still_red_wine = db.Column(db.Boolean)
    sparkly_white_wine = db.Column(db.Boolean)
    sparkly_rose_wine = db.Column(db.Boolean)
    sparkly_red_wine = db.Column(db.Boolean)

    def __repr__(self):
        return '<AOC {}>'.format(self.name)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_type = db.Column(db.String(140), index=True)
    score = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_over = db.Column(db.Boolean, default=False)

    def increment_score(self):
        self.score += 1


def get_player_stats(user_):
    games = Game.query.filter_by(player_id=user_.id).all()
    games_per_type = {}
    for game_type, game_name in current_app.config['GAMES_TO_NAMES'].items():
        games_per_type[(game_type, game_name)] = [game for game in games if game.game_type == game_type]

    summary_per_type = []
    for (game_type, game_name), games in games_per_type.items():
        summary_per_type.append(
            {
                'name': game_name,
                'type': game_type,
                'nb_played': len(games),
                'best': max(games, key=lambda x: x.score).score if len(games) > 0 else '-'
            }
        )

        return summary_per_type, len(games)
