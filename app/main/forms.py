from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, SelectField, BooleanField, IntegerField, \
    SelectMultipleField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class NewGameForm(FlaskForm):
    game_type = SelectField(_('Game type'),
                            choices=[('quiz_grape_color', _('Grape Color Quiz')),
                                     ('quiz_grape_region', _('Grape Region Quiz')),
                                     ('quiz_aoc_color', _('AOC Color Quiz')),
                                     ('quiz_aoc_region', _('AOC Region Quiz'))])
    submit = SubmitField(_('Start a game'))


class EditGrapeForm(FlaskForm):
    id = IntegerField('ID')
    name = TextAreaField('Name')
    regions = TextAreaField('Regions')
    vineyards = RadioField('Vineyards', choices=[('quiz_grape_color', _('Grape Color Quiz')),
                                                 ('quiz_grape_region', _('Grape Region Quiz')),
                                                 ('quiz_aoc_color', _('AOC Color Quiz')),
                                                 ('quiz_aoc_region', _('AOC Region Quiz'))])
    departments = TextAreaField('Departments')
    area_fr = IntegerField('Area in France')
    area_world = IntegerField('Area in the world')
    red = BooleanField('is red')
    submit = SubmitField()


class EditUserForm(FlaskForm):
    username = TextAreaField(label='Username', default='')
    email = TextAreaField(label=_l('Email'), default='')
    password = PasswordField(_l('Password'), default='')
    password2 = PasswordField(
        _l('Repeat Password'),  default='', validators=[EqualTo('password')])
    about_me = TextAreaField(label=_l('About me'), default='')
    submit = SubmitField(_('Edit User'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.user = User.query.filter_by(username=original_username).first_or_404()
        self.username.default = self.user.username
        self.email.default = self.email
        if self.user.about_me is not None:
            self.about_me.label.text = self.user.about_me

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


