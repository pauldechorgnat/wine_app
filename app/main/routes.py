#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, NewGameForm
from app.models import User, Post, Cepage, AOC, Game
from app.translate import translate
from app.main import bp
import random


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

    # @bp.route('/explore')
    # @login_required
    # def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    if request.method == 'POST':
        if request.form['submit-button'] == 'Grapes':
            return redirect(url_for('main.explore_grapes'))
        elif request.form['submit-button'] == 'Vineyards':
            return redirect(url_for('main.explore_vineyards'))
    return render_template('explore.html')


@bp.route('/explore_grapes')
@login_required
def explore_grapes():
    page = request.args.get('page', 1, type=int)
    grapes = Cepage.query.order_by(Cepage.id.asc()).paginate(
        page, current_app.config['GRAPES_PER_PAGE'], False)
    next_url = url_for('main.explore_grapes', page=grapes.next_num) \
        if grapes.has_next else None
    prev_url = url_for('main.explore_grapes', page=grapes.prev_num) \
        if grapes.has_prev else None
    return render_template('explore_grapes.html',
                           title=_('Explore Grapes'),
                           grapes=grapes.items,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore_aocs')
@login_required
def explore_aocs():
    page = request.args.get('page', 1, type=int)
    aocs = AOC.query.order_by(AOC.id.asc()).paginate(
        page, current_app.config['AOC_PER_PAGE'], False)
    next_url = url_for('main.explore_aocs', page=aocs.next_num) \
        if aocs.has_next else None
    prev_url = url_for('main.explore_aocs', page=aocs.prev_num) \
        if aocs.has_prev else None
    return render_template('explore_aocs.html',
                           title=_('Explore AOCs'),
                           aocs=aocs.items,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@bp.route('/new_game', methods=['GET', 'POST'])
@login_required
def new_game():
    form = NewGameForm()

    if form.validate_on_submit():
        # creating a new game
        new_game_ = Game(player_id=current_user.id)

        if form.game_type.data == 'quiz_grape_color':

            flash(_('New game of Grape Color Quiz'))

            grape_ids = Cepage.query.with_entities(Cepage.id).all()

            new_game_.game_type = 'Grape Color Quiz'
            db.session.add(new_game_)
            db.session.commit()

            return redirect(url_for('main.quiz_grape_color',
                                    grape_id=random.choice(grape_ids)[0],
                                    game_id=new_game_.id))
        elif form.game_type.data == 'quiz_grape_region':
            flash(_('New game of Grape Region Quiz'))
            grape_ids = Cepage.query.with_entities(Cepage.id).all()

            new_game_.game_type = 'Grape Region Quiz'
            db.session.add(new_game_)
            db.session.commit()

            return redirect(url_for('main.quiz_grape_region',
                                    grape_id=random.choice(grape_ids)[0],
                                    game_id=new_game_.id))
        elif form.game_type.data == 'quiz_aoc_region':
            flash(_('New game of AOC Region Quiz'))
            aoc_ids = AOC.query.with_entities(AOC.id).all()

            new_game_.game_type = 'AOC Region Quiz'
            db.session.add(new_game_)
            db.session.commit()

            return redirect(url_for('main.quiz_aoc_region',
                                    aoc_id=random.choice(aoc_ids)[0],
                                    game_id=new_game_.id))

        elif form.game_type.data == 'quiz_aoc_color':
            flash(_('New game of AOC Color Quiz'))
            aoc_ids = AOC.query.with_entities(AOC.id).all()

            new_game_.game_type = 'AOC Color Quiz'
            db.session.add(new_game_)
            db.session.commit()

            return redirect(url_for('main.quiz_aoc_color',
                                    aoc_id=random.choice(aoc_ids)[0],
                                    game_id=new_game_.id))

        else:
            flash(_('Not implemented yet...'))

    return render_template('new_game.html', title=_('Launch a new game!'), form=form)


def right_answer(game):
    flash(_('Right answer'))
    game.increment_score()
    db.session.add(game)
    db.session.commit()


def wrong_answer(game):
    flash(_('Wrong answer'))
    game.is_over = True
    db.session.add(game)
    post = Post(
        body="I just scored {} at {}!".format(game.score, game.game_type),
        author=current_user,
        language='en')
    db.session.add(post)
    db.session.commit()


@bp.route('/quiz_grape_color/<game_id>/<grape_id>', methods=['GET', 'POST'])
@login_required
def quiz_grape_color(game_id, grape_id):
    # getting the game
    current_game = Game.query.filter_by(id=game_id).first_or_404()
    if current_game.is_over:
        return redirect(url_for('main.new_game'))

    # getting the grape
    random_grape = Cepage.query.filter_by(id=grape_id).first_or_404()
    true_red = random_grape.red
    grape_name = random_grape.name
    grape_id = random_grape.id

    if request.method == 'POST':
        if request.form['submit-button'] == 'Red':
            if true_red:
                right_answer(current_game)
                grape_ids = Cepage.query.with_entities(Cepage.id).all()
                return redirect(url_for('main.quiz_grape_color',
                                        grape_id=random.choice(grape_ids)[0],
                                        game_id=current_game.id))
            else:
                wrong_answer(current_game)
                return redirect(url_for('main.grape_identity_card',
                                        grape_id=grape_id))
        elif request.form['submit-button'] == 'White':

            if not true_red:
                right_answer(current_game)
                grape_ids = Cepage.query.with_entities(Cepage.id).all()
                return redirect(url_for('main.quiz_grape_color',
                                        grape_id=random.choice(grape_ids)[0],
                                        game_id=current_game.id))
            else:
                wrong_answer(current_game)
                return redirect(url_for('main.grape_identity_card', grape_id=grape_id))

    elif request.method == 'GET':
        return render_template('red_or_white.html', title='Grape - Color Quiz', grape_name=grape_name)


@bp.route('/grape_identity_card/<grape_id>', methods=['GET', 'POST'])
@login_required
def grape_identity_card(grape_id):
    grape = Cepage.query.filter_by(id=grape_id).first_or_404()
    max_id = Cepage.query.order_by(Cepage.id.desc()).first().id
    min_id = Cepage.query.order_by(Cepage.id.asc()).first().id
    grape_id_num = int(grape_id)
    next_url = None if max_id == grape_id_num else url_for('main.grape_identity_card', grape_id=grape_id_num + 1)
    prev_url = None if min_id == grape_id_num else url_for('main.grape_identity_card', grape_id=grape_id_num - 1)

    true_red = grape.red
    grape_name = grape.name
    grape_region = grape.regions
    grape_ss_region = grape.sous_regions

    grape_super_fr = grape.superficie_france
    grape_super_fr = 'NC' if grape_super_fr is None else grape_super_fr
    grape_super_monde = grape.superficie_monde
    grape_super_monde = 'NC' if grape_super_monde is None else grape_super_monde

    return render_template('grape_identity_card.html', true_red=true_red, grape_name=grape_name,
                           grape_super_fr=grape_super_fr, grape_super_monde=grape_super_monde,
                           grape_region=grape_region, grape_ss_region=grape_ss_region,
                           title=grape_name,
                           prev_url=prev_url,
                           next_url=next_url)


@bp.route('/aoc_identity_card/<aoc_id>', methods=['GET', 'POST'])
@login_required
def aoc_identity_card(aoc_id):
    aoc = AOC.query.filter_by(id=aoc_id).first_or_404()
    aoc_name = aoc.name
    aoc_vineyard = aoc.vignoble

    red = aoc.vin_effervescent_rouge or aoc.vin_tranquille_rouge
    white = aoc.vin_effervescent_blanc or aoc.vin_tranquille_blanc

    max_id = AOC.query.order_by(AOC.id.desc()).first().id
    min_id = AOC.query.order_by(AOC.id.asc()).first().id
    aoc_id_num = int(aoc_id)
    next_url = None if max_id == aoc_id_num else url_for('main.aoc_identity_card', aoc_id=aoc_id_num + 1)
    prev_url = None if min_id == aoc_id_num else url_for('main.aoc_identity_card', aoc_id=aoc_id_num - 1)

    return render_template('aoc_identity_card.html',
                           red=red,
                           white=white,
                           aoc_name=aoc_name,
                           aoc_vineyard=aoc_vineyard,
                           title=aoc_name,
                           prev_url=prev_url,
                           next_url=next_url)


def clean_vineyard(vineyard):
    return vineyard.lower().replace(u'ô', 'o'). \
        replace(u'val de ', '').replace(u'lorraine', 'champagne'). \
        replace(u'vallée du ', '').replace(u'-roussillon', ''). \
        replace(u'-bugey', '').replace(u'lyonnais', 'rhone'). \
        replace(u'beaujolais', 'bourgogne').replace(u'limousin', 'sud-ouest'). \
        replace(u'charentes', 'bordeaux').replace(u' ', '')


@bp.route('/quiz_grape_region/<game_id>/<grape_id>', methods=['GET', 'POST'])
@login_required
def quiz_grape_region(game_id, grape_id):
    # getting the game
    current_game = Game.query.filter_by(id=game_id).first_or_404()
    if current_game.is_over:
        return redirect(url_for('main.new_game'))

    grape = Cepage.query.filter_by(id=grape_id).first_or_404()
    grape_name = grape.name
    clean_vineyards = clean_vineyard(grape.vignobles)
    list_of_vineyards = [
        'alsace',
        'armagnac',
        'bordeaux',
        'bourgogne',
        'champagne',
        'cognac',
        'corse',
        'jura',
        'languedoc',
        'loire',
        'provence',
        'rhone',
        'savoie',
        'sud-ouest',
    ]
    list_of_positive_vineyards = []
    list_of_negative_vineyards = []

    for vineyard in list_of_vineyards:
        if vineyard in clean_vineyards:
            list_of_positive_vineyards.append(vineyard)
        else:
            list_of_negative_vineyards.append(vineyard)

    # si les informations ne sont pas présentes on change de cépage
    if len(list_of_positive_vineyards) == 0 or len(list_of_negative_vineyards) == 0:
        grape_ids = Cepage.query.with_entities(Cepage.id).all()
        return redirect(url_for('main.quiz_grape_region',
                                grape_id=random.choice(grape_ids)[0],
                                game_id=current_game.id))
    else:
        positive_vineyard = random.choice(list_of_positive_vineyards)
        negative_vineyard = random.choice(list_of_negative_vineyards)

        left_vineyard, right_vineyard = random.sample([positive_vineyard, negative_vineyard], k=2)

    if request.method == 'POST':
        clicked_is_positive = next(request.form.keys()).replace('.x', '')

        if clicked_is_positive == 'True':
            right_answer(current_game)
            grape_ids = Cepage.query.with_entities(Cepage.id).all()
            return redirect(url_for('main.quiz_grape_region',
                                    grape_id=random.choice(grape_ids)[0],
                                    game_id=current_game.id))
        else:
            wrong_answer(current_game)
            return redirect(url_for('main.grape_identity_card', grape_id=grape_id))
    elif request.method == 'GET':

        return render_template('region_quizz.html', left_vineyard=left_vineyard,
                               right_vineyard=right_vineyard,
                               left_is_positive=positive_vineyard == left_vineyard,
                               right_is_positive=positive_vineyard == right_vineyard,
                               grape_name=grape_name,
                               title='Grape - Region Quiz')


@bp.route('/quiz_aoc_region/<game_id>/<aoc_id>', methods=['GET', 'POST'])
@login_required
def quiz_aoc_region(game_id, aoc_id):
    # getting the game
    current_game = Game.query.filter_by(id=game_id).first_or_404()
    if current_game.is_over:
        return redirect(url_for('main.new_game'))

    aoc = AOC.query.filter_by(id=aoc_id).first_or_404()
    aoc_name = aoc.name.split(' ou')[0]
    aoc_vineyard = aoc.vignoble

    list_of_vineyards = [
        'alsace',
        'armagnac',
        'bordeaux',
        'bourgogne',
        'champagne',
        'cognac',
        'corse',
        'jura',
        'languedoc',
        'loire',
        'provence',
        'rhone',
        'savoie',
        'sud-ouest',
    ]

    positive_vineyard = clean_vineyard(aoc_vineyard)

    list_of_vineyards.remove(positive_vineyard)
    negative_vineyard = random.choice(list_of_vineyards)
    left_vineyard, right_vineyard = random.sample([positive_vineyard, negative_vineyard], k=2)

    if request.method == 'POST':
        clicked_is_positive = next(request.form.keys()).replace(u'.x', '')
        if clicked_is_positive == 'True':
            aoc_ids = AOC.query.with_entities(AOC.id).all()
            right_answer(current_game)
            return redirect(url_for('main.quiz_aoc_region',
                                    aoc_id=random.choice(aoc_ids)[0],
                                    game_id=current_game.id))
        else:
            wrong_answer(current_game)
            return redirect(url_for('main.aoc_identity_card', aoc_id=aoc_id))

    return render_template('region_quizz.html',
                           left_vineyard=left_vineyard,
                           right_vineyard=right_vineyard,
                           grape_name=aoc_name,
                           left_is_positive=left_vineyard == positive_vineyard,
                           right_is_positive=right_vineyard == positive_vineyard,
                           title='AOC - Region Quiz')


@bp.route('/quiz_aoc_color/<game_id>/<aoc_id>', methods=['GET', 'POST'])
@login_required
def quiz_aoc_color(game_id, aoc_id):
    # getting the game
    current_game = Game.query.filter_by(id=game_id).first_or_404()
    if current_game.is_over:
        return redirect(url_for('main.new_game'))

    # getting the grape
    random_aoc = AOC.query.filter_by(id=aoc_id).first_or_404()
    red = random_aoc.vin_effervescent_rouge or random_aoc.vin_tranquille_rouge
    white = random_aoc.vin_effervescent_blanc or random_aoc.vin_tranquille_blanc or \
            random_aoc.vin_effervescent_rose or random_aoc.vin_tranquille_rose
    aoc_name = random_aoc.name

    if request.method == 'POST':
        if request.form['submit-button'] == 'Red':
            if red:
                right_answer(current_game)
                aoc_ids = AOC.query.with_entities(AOC.id).all()
                return redirect(url_for('main.quiz_aoc_color',
                                        aoc_id=random.choice(aoc_ids)[0],
                                        game_id=current_game.id))
            else:
                wrong_answer(current_game)
                return redirect(url_for('main.aoc_identity_card',
                                        aoc_id=aoc_id))
        elif request.form['submit-button'] == 'White':

            if white:
                right_answer(current_game)
                aoc_ids = AOC.query.with_entities(AOC.id).all()
                return redirect(url_for('main.quiz_aoc_color',
                                        aoc_id=random.choice(aoc_ids)[0],
                                        game_id=current_game.id))
            else:
                wrong_answer(current_game)
                return redirect(url_for('main.aoc_identity_card', aoc_id=aoc_id))
        else:
            raise TypeError
    elif request.method == 'GET':
        return render_template('red_or_white.html',
                               title='AOC - Color Quiz',
                               grape_name=aoc_name)
