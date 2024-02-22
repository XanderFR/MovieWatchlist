from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, URLField, PasswordField  # Fields for the form
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo  # Ensure no blank fields, or nonsensical number values


class MovieForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    director = StringField("Director", validators=[InputRequired()])
    year = IntegerField("Year",
                        validators=[
                            InputRequired(),
                            NumberRange(min=1878, message="Please enter a year in the format YYYY.")])
    submit = SubmitField("Add Movie")


class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    def processFormdata(self, valuelist):
        # Checks valuelist contains at least 1 element, and the first element isn't falsy (i.e. empty string)
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]  # Takes text in textarea, splits it into lines, strips lines of whitespace and puts into list that gets assigned to self.data
        else:  # No valuelist or is empty
            self.data = []


class ExtendedMovieForm(MovieForm):
    cast = StringListField("Cast")
    series = StringListField("Series")
    tags = StringListField("Tags")
    description = TextAreaField("Description")
    video_link = URLField("Video link")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])

    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(
                min=4,
                max=20,
                message="Your password must be between 4 and 20 characters long.",
            ),
        ],
    )

    confirmPassword = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo(
                "password",
                message="This password did not match the one in the password field.",
            ),
        ],
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")
