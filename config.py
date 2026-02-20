import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # for email errors
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'  # True if '1'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'shrvs.practice@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'fzgs utkx jwbw oafn')  # App password for Gmail
    ADMINS = ['shrvs.practice@gmail.com']

    # for post per pages
    POSTS_PER_PAGE = 3
    # for different languages
    LANGUAGES = ['en', 'es', 'fil_PH']

