from flask_security.forms import RegisterForm, Required
from flask_wtf import RecaptchaField
from wtforms import TextField

class ExtendedRegisterForm(RegisterForm):
    name = TextField('Name', [Required()])
    recaptcha = RecaptchaField()