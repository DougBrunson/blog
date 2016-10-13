from basehandler import BaseHandler
from utils import *
from models import *

class Signup(BaseHandler):

    def get(self):
        self.render("signup.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify_password')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "Invalid username"
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "Invalid password"
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Passwords don't match"
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "Invalid email"
            have_error = True

        print 'signup: '
        print 'have_err: ', have_error

        if have_error:
            self.render('signup.html', **params)


        print "entering reg copy"
        u = User.by_name(self.username)
        if u:
            print 'if block'
            self.render('signup.html', error_username="Username already taken")
        else:

            print 'else block'
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


class Register(Signup):

    def done(self):
        # make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            self.render('signup.html', error_username="Username already taken")
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


class Login(BaseHandler):

    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            self.render('login.html', error="Invalid login")


class Logout(BaseHandler):

    def get(self):
        self.logout()
        self.redirect('/')
