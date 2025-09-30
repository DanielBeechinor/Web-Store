from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, IntegerField
from wtforms.validators import InputRequired, NumberRange, EqualTo


class RegistrationForm(FlaskForm):
    user_id = StringField('User id:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    password2 = PasswordField('Confirm Password:', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    user_id = StringField('User id', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Submit')

class FilterForm(FlaskForm):
    variety = RadioField(choices=['Food', 'Drink', 'Both'],
                         default='Both')
    alcoholic = RadioField(choices=['Alcoholic', 'Non-Alcoholic', 'Both'],
                           default='Both')
    submit = SubmitField('Filter')

class CheckoutForm(FlaskForm):
    table_number = IntegerField('Table Number', validators=[InputRequired(), NumberRange(0, 20)])

    payment_method = RadioField(choices=['Cash', 'Card'],
                                default='Cash')
    
    submit = SubmitField('Checkout')

class AddProductForm(FlaskForm):
    name = StringField('What is the name of the product?', validators=[InputRequired()])
    price = StringField('What does the product cost?', validators=[InputRequired()])
    alcoholic = RadioField('Does this product contain alcohol?',
                        choices=['Alcoholic', 'Non-Alcoholic'],
                        default='Non-Alcoholic')
    type = RadioField('What type of product is this?', 
                      choices=['Food', 'Drink'],
                      default='Food')
    picture = StringField('Pathname of image *if left blank a default will be used')
    submit = SubmitField('Add Product')

class UpdatePriceForm(FlaskForm):
    price = StringField('New price', validators=[InputRequired()])

    submit = SubmitField('Change')