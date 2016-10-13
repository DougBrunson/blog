import os
import webapp2
import jinja2
from urlparse import urlparse

from utils import *
from auth import *
from models import *
from basehandler import BaseHandler


class Index(BaseHandler):

    """Index docstring"""

    def get(self):
        posts = Post.all()
        self.render('index.html', posts=posts, user=self.user)


# -------------------------- post crud ------------------------------------
class DisplayPost(BaseHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        comments = Comment.all().filter('post_id = ', int(post_id))
        self.render("post.html",
                    post=post,
                    comments=comments,
                    likes=len(post.likes))


class NewPost(BaseHandler):

    def get(self):
        if not self.user:
            self.redirect('/login')
        else:
            self.render('new_post.html')

    def post(self):
        if self.user:
            subject = self.request.get("subject")
            content = self.request.get("content")

            if subject and content:
                p = Post(subject=subject,
                         content=content,
                         author=self.user.username)
                p.put()
                self.redirect('/')
            else:
                self.redirect('/post/new')
        else:
            self.redirect('/login')


class DeletePost(BaseHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        if self.user and self.user.username == post.author:
            post.delete()
            self.redirect('/')
        else:
            self.redirect('/login')


class EditPost(BaseHandler):

    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id))
            post = db.get(key)

            if self.user.username == post.author:
                self.render('edit_post.html', post=post)

            else:
                return self.error(403)
        else:
            self.redirect('/login')

    def post(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id))
            post = db.get(key)

            if self.user.username == post.author:
                post.subject = self.request.get('subject')
                post.content = self.request.get('content')
                post.put()
                self.redirect('/post/%s' % str(post.key().id()))
            else:
                return self.error(403)
        else:
            self.redirect('/login')


# -------------------------- comment crud ------------------------------------
class NewComment(BaseHandler):

    def get(self, post_id):
        if not self.user:
            self.redirect('/login')
        else:
            key = db.Key.from_path('Post', int(post_id))
            post = db.get(key)
            self.render('new_comment.html', p=post)

    def post(self, post_id):
        if self.user:
            content = self.request.get("content")

            if content:
                c = Comment(parent=blog_key(),
                            content=content,
                            author=self.user.username,
                            post_id=int(post_id))
                c.put()
                self.redirect('/post/%s' % str(post_id))
        else:
            self.redirect('/login')


class EditComment(BaseHandler):

    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Comment', int(post_id), parent=blog_key())
            comment = db.get(key)

            if self.user.username == comment.author:
                content = comment.content
                self.render('edit_comment.html', comment=comment)

            else:
                return self.error(403)
        else:
            self.redirect('/login')

    def post(self, comment_id):
        if self.user:
            key = db.Key.from_path(
                'Comment', int(comment_id), parent=blog_key())
            comment = db.get(key)

            if self.user.username == comment.author:
                comment.content = self.request.get('content')
                comment.put()

                key = db.Key.from_path('Post', int(comment.post_id))
                post = db.get(key)
                self.redirect('/post/%s' % str(post.key().id()))
            else:
                return self.error(403)
        else:
            self.redirect('/login')


class DeleteComment(BaseHandler):

    def get(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comment = db.get(key)

        if self.user and self.user.username == comment.author:
            comment.delete()
            self.redirect('/')
        else:
            self.redirect('/login')


class Like(BaseHandler):

    def post(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id))
            post = db.get(key)

            u = self.user.username

            if u != post.author and u not in post.likes:
                post.likes.append(u)
                post.put()
            self.redirect('/post/%s' % str(post.key().id()))


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/post/([0-9]+)', DisplayPost),
    ('/post/new', NewPost),
    ('/post/([0-9]+)/edit', EditPost),
    ('/post/([0-9]+)/delete', DeletePost),
    ('/post/([0-9]+)/comment', NewComment),
    ('/comment/([0-9]+)/edit', EditComment),
    ('/comment/([0-9]+)/delete', DeleteComment),
    ('/post/([0-9]+)/like', Like),
    ('/signup', Signup),
    ('/login', Login),
    ('/logout', Logout),
], debug=True)
