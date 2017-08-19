# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.conf import settings
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from datetime import datetime
from .forms import SignupForm,LoginForm,PostForm,LikeForm,CommentForm
from django.contrib.auth.hashers import make_password,check_password
from .models import UserModel,SessionToken,PostModel,LikeModel,CommentModel
from imgurpython import ImgurClient
from goofy.settings import BASE_DIR
from django.contrib import messages


# Create your views here.
def signup_view(request):
    today = datetime.now()
    if request.method == "GET":
        form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            hashed_password = make_password(password)
            user = UserModel(name = name,email = email, username = username, password = make_password(password))
            user.save()



            subject = 'site conact form'
            from_email = settings.EMAIL_HOST_USER
            to_email = email,
            # to_email = [from_email,'email']
            contact_message = "%s:%s via %s"%(name,username,to_email)
            html_message = '<h1> welcome</h1>'
            
            send_mail(subject,
                      contact_message,
                      from_email,
                      to_email,
                      html_message = html_message,
                      fail_silently = True
                      )




            messages.success(request, 'your account has been created successfully.')
            return render(request, "signup.html")




    return render(request, "signup.html",{
        "today":today,
        "method":request.method,
        "form":form
    })

def login_view(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html",{
            "form":form
        })
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = UserModel.objects.filter(username = username).first()

            if user:
                if check_password(password,user.password):
                    session = SessionToken(user = user)
                    session.create_token()
                    session.save()
                    response = redirect("/feed")
                    response.set_cookie(key= "session_token",value=session.session_token)
                    return response
                    print "user is valid"
                else:
                    "user is invalid"
                    messages.success(request, 'Username and password is incorrect.')
                    return render(request, "login.html")

def check_validation(request):
  if request.COOKIES.get('session_token'):
    session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
    if session:
      return session.user
  else:
    return None


def post_view(request):
    user = check_validation(request)

    if user:
        print 'Authentic user'
    else:
        return redirect('/login/')

    if request.method=="GET":
        form = PostForm
        return render(request, "post.html",{
            "form":form
        })


    elif request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get('image')
            caption = form.cleaned_data.get('caption')
            post = PostModel(user=user, image=image, caption=caption)
            post.save()
            path = str(BASE_DIR + "\\" + post.image.url)
            client = ImgurClient("b82c694efc44901", "d3209f7bd4e3489aca68240c25a2531db912a546")
            post.image_url = client.upload_from_path(path,anon=True)['link']


            post.save()
            messages.success(request, 'Your post has been created suceessfully.')
            return render(request, "post.html")
            return redirect("/feed")




def feed(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by("-created_on").filter(user=user)
        return render(request, 'feed.html', {
            "posts" : posts
        })
    else:
        return redirect('/login/')
def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id

            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()

            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()

            return redirect('/feed/')
    else:
     return redirect('/login/')



def comment_view(request):
   user = check_validation(request)
   if user and request.method == 'POST':
     form = CommentForm(request.POST)
     if form.is_valid():
       post_id = form.cleaned_data.get('post').id
       comment_text = form.cleaned_data.get('comment_text')
       comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
       comment.save()
       return redirect('/feed/')
     else:
         return redirect('/feed/')
   else:
     return redirect('/login')


def validate_password_strength(value):
    """Validates that a password is as least 10 characters long and has at least
    2 digits and 1 Upper case letter.
    """
    min_length = 10

    if len(value) < min_length:
        raise ValidationError(_('Password must be at least {5} characters '
                                'long.').format(min_length))

