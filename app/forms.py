from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, ValidationError

class RightLength(object):
    """
    Largely modeled on the EqualTo validator
    """
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        max_len = len(other.data.split())
        if (field.data > max_len) or (field.data < 1):
            raise ValidationError('Length should be between 1 and length of sentence ({})'
                                  .format(max_len))

class NumberOfWords(object):
    def __init__(self, max_len):
        self.max_len = max_len

    def __call__(self, form, field):
        sentence_len = len(field.data.split())
        if (self.max_len < sentence_len):
            raise ValidationError('Sentence cannot be more than {} words long.'
                                  .format(self.max_len))

class MemeForm(FlaskForm):
    sentence = TextAreaField('Sentence',
                             validators=[DataRequired(), NumberOfWords(10)])
    max_length = IntegerField('Max Length (Optional)',
                              validators=[Optional(), RightLength('sentence')])
    submit = SubmitField('Submit')
