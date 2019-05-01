#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, NewGameForm, RedForm, WhiteForm, LeftForm, RightForm
from app.models import User, Post, Cepage, AOC
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


@bp.route('/explore')
@login_required
def explore():
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
        if form.game_type.data == 'quiz_grape_color':

            flash(_('New game of Grape Color Quiz'))
            cepage_ids = Cepage.query.with_entities(Cepage.id).all()
            print(cepage_ids)
            return redirect(url_for('main.quiz_grape_color', cepage_id=random.choice(cepage_ids)[0]))
        elif form.game_type.data == 'quiz_grape_region':
            flash(_('New game of Grape Region Quiz'))
            cepage_ids = Cepage.query.with_entities(Cepage.id).all()
            return redirect(url_for('main.quiz_grape_region', cepage_id=random.choice(cepage_ids)[0]))
        elif form.game_type.data == 'quiz_aoc_region':
            flash(_('New game of AOC Region Quiz'))
            aoc_ids = AOC.query.with_entities(AOC.id).all()
            return redirect(url_for('main.quiz_aoc_region', aoc_id=random.choice(aoc_ids)[0]))
        else:
            flash(_('Not implemented yet...'))

    return render_template('new_game.html', title=_('Launch a new game!'), form=form)


@bp.route('/quiz_grape_color/<cepage_id>', methods=['GET', 'POST'])
@login_required
def quiz_grape_color(cepage_id):
    random_cepage = Cepage.query.filter_by(id=cepage_id).first_or_404()
    true_red = random_cepage.red
    cepage_name = random_cepage.name
    cepage_id = random_cepage.id

    if request.method == 'POST':
        if request.form['submit-button'] == 'Red':
            if true_red:
                flash(_('Right answer'))
                cepage_ids = Cepage.query.with_entities(Cepage.id).all()
                return redirect(url_for('main.quiz_grape_color', cepage_id=random.choice(cepage_ids)[0]))
            else:
                flash(_('Wrong answer'))
                post = Post(
                    body="Aie Caramba ! Je me suis encore trompé sur {} au jeu des couleurs !".format(cepage_name),
                    author=current_user,
                    language='fr')
                db.session.add(post)
                db.session.commit()
                return redirect(url_for('main.grape_identity_card', cepage_id=cepage_id))
        elif request.form['submit-button'] == 'White':

            if not true_red:
                flash(_('Right answer'))
                cepage_ids = Cepage.query.with_entities(Cepage.id).all()
                return redirect(url_for('main.quiz_grape_color', cepage_id=random.choice(cepage_ids)[0]))
            else:
                flash(_('Wrong answer'))
                post = Post(
                    body="Aie Caramba ! Je me suis encore trompé sur {} au jeu des couleurs !".format(cepage_name),
                    author=current_user,
                    language='fr')
                db.session.add(post)
                db.session.commit()
                return redirect(url_for('main.grape_identity_card', cepage_id=cepage_id))
        else:
            raise TypeError
    elif request.method == 'GET':
        return render_template('red_or_white.html', title='Red or White', cepage_name=cepage_name)


@bp.route('/grape_identity_card/<cepage_id>', methods=['GET', 'POST'])
@login_required
def grape_identity_card(cepage_id):
    cepage = Cepage.query.filter_by(id=cepage_id).first_or_404()
    true_red = cepage.red
    cepage_name = cepage.name
    cepage_region = cepage.regions
    cepage_ss_region = cepage.sous_regions

    cepage_super_fr = cepage.superficie_france
    cepage_super_fr = 'NC' if cepage_super_fr is None else cepage_super_fr
    cepage_super_monde = cepage.superficie_monde
    cepage_super_monde = 'NC' if cepage_super_monde is None else cepage_super_monde
    return render_template('grape_identity_card.html', true_red=true_red, cepage_name=cepage_name,
                           cepage_super_fr=cepage_super_fr, cepage_super_monde=cepage_super_monde,
                           cepage_region=cepage_region, cepage_ss_region=cepage_ss_region)


def clean_vineyard(vineyard):
    return vineyard.lower().replace('ô', 'o'). \
        replace('val de ', '').replace('lorraine', 'champagne'). \
        replace('vallée du ', '').replace('-roussillon', ''). \
        replace('-bugey', '').replace('lyonnais', 'rhone'). \
        replace('beaujolais', 'bourgogne').replace('limousin', 'sud-ouest'). \
        replace('charentes', 'bordeaux').replace(' ', '')


@bp.route('/quiz_grape_region/<cepage_id>', methods=['GET', 'POST'])
@login_required
def quiz_grape_region(cepage_id):
    cepage = Cepage.query.filter_by(id=cepage_id).first_or_404()
    cepage_name = cepage.name
    cepage_regions = cepage.regions
    clean_vineyards = clean_vineyard(cepage.vignobles)
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
        cepage_ids = Cepage.query.with_entities(Cepage.id).all()
        return redirect(url_for('main.quiz_grape_region', cepage_id=random.choice(cepage_ids)[0]))
    else:
        positive_vineyard = random.choice(list_of_positive_vineyards)
        negative_vineyard = random.choice(list_of_negative_vineyards)

        left_vineyard, right_vineyard = random.sample([positive_vineyard, negative_vineyard], k=2)

    if request.method == 'POST':
        clicked_is_positive = next(request.form.keys()).replace('.x', '')

        if clicked_is_positive == 'True':
            flash(_('Right answer'))
            cepage_ids = Cepage.query.with_entities(Cepage.id).all()
            return redirect(url_for('main.quiz_grape_region', cepage_id=random.choice(cepage_ids)[0]))
        else:
            flash(_('Wrong answer'))
            post = Post(
                body="Aie Caramba ! Je me suis encore trompé sur {} au jeu des vignobles !".format(cepage_name),
                author=current_user,
                language='fr')
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('main.grape_identity_card', cepage_id=cepage_id))
    elif request.method == 'GET':

        return render_template('region_quizz.html', left_vineyard=left_vineyard,
                               right_vineyard=right_vineyard,
                               left_is_positive=positive_vineyard == left_vineyard,
                               right_is_positive=positive_vineyard == right_vineyard,
                               cepage_name=cepage_name)


@bp.route('/quiz_aoc_region/<aoc_id>', methods=['GET', 'POST'])
@login_required
def quiz_aoc_region(aoc_id):
    aoc = AOC.query.filter_by(id=aoc_id).first_or_404()
    aoc_name = aoc.name.split(' ou')[0]
    aoc_vineyard = aoc.vignoble
    aocs = AOC.query.all()

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
        clicked_is_positive = next(request.form.keys()).replace('.x', '')
        if clicked_is_positive == 'True':
            flash(_('Right answer'))
            aoc_ids = AOC.query.with_entities(AOC.id).all()
            return redirect(url_for('main.quiz_aoc_region', aoc_id=random.choice(aoc_ids)[0]))
        else:
            flash(_('Wrong answer'))
            post = Post(
                body="Aie Caramba ! Je me suis encore trompé sur {} au jeu des vignobles (AOC) !".format(aoc_name),
                author=current_user,
                language='fr')
            db.session.add(post)
            db.session.commit()
            # return redirect(url_for('main.identity_card', cepage_id=aoc_id))
            aoc_ids = AOC.query.with_entities(AOC.id).all()
            return redirect(url_for('main.quiz_aoc_region', aoc_id=random.choice(aoc_ids)[0]))

    return render_template('region_quizz.html',
                           left_vineyard=left_vineyard,
                           right_vineyard=right_vineyard,
                           cepage_name=aoc_name,
                           left_is_positive=left_vineyard == positive_vineyard,
                           right_is_positive=right_vineyard == positive_vineyard)
