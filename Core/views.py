import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowerCount
from itertools import chain

# Create your views here.

#
@login_required(login_url='signin')
def index(request):
    # get all active users
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # filter all people subscribed
    user_following_list = []
    user_following = FollowerCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)

    # filter all subscribed people's post
    posts = []
    for usernames in user_following_list:
        feed_list = Post.objects.filter(user=usernames)
        posts.append(feed_list)

    post_list = list(chain(*posts))

    # filter all potential people to subscribe
    user_following_all = []
    all_users = User.objects.all()
    for users in user_following:
        user_list = User.objects.get(username=users.user)
        user_following_all.append(user_list)

    # get rid of already subscribed
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]

    # get rid of self
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]

    # random order
    random.shuffle(final_suggestions_list)

    # get user info from final_suggestions_list
    # get id
    id_profile_list = []
    for users in final_suggestions_list:
        id_profile_list.append(users.id)

    username_profile_list = []
    for id in id_profile_list:
        profile_info = Profile.objects.filter(id_user=id)
        username_profile_list.append(profile_info)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'index.html', {'user_profile':user_profile, 'posts':post_list,
                                          'suggestions_username_profile_list':
                                              suggestions_username_profile_list[:4]})

#
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # verify
        user = auth.authenticate(username=username, password=password)

        # if user exists
        if user is not None:
            # messages.info(request, "Successfully Logged In")
            auth.login(request, user)
            return redirect('/')
        # if user does not exist
        else:
            messages.info(request, "Unable to Log In")
            return redirect('signin')

    else:
        return render(request, 'signin.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # match passwords
        if password == password2:
            # if email already exist
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect('signup')

            # if username already exist
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect('signup')

            # if none exists
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # messages.info(request, "Successfully Signed Up")

                # login
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # set default personal info
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()

                return redirect('settings')

        else:
            messages.info(request, "Passwords Do Not Match")
            return redirect('signup')

    else:
        return render(request, 'signup.html')


#
@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        # if no avatar is uploaded
        if not request.FILES.get('image'):
            # image = user_profile.profileing
            # bio = request.POST['bio']
            # location = request.POST['location']

            # user_profile.profileing = image
            user_profile.bio = request.POST['bio']
            user_profile.location = request.POST['location']
            user_profile.save()

        # if an avatar is detected
        if request.FILES.get('image'):
            user_profile.profileing = request.FILES.get('image')
            user_profile.bio = request.POST['bio']
            user_profile.location = request.POST['location']
            user_profile.save()

        return redirect('settings')

    return render(request, 'settings.html', {'user_profile':user_profile})

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        # icontains -> ignore capitalization
        username_object = User.objects.filter(username__icontains=username)

        id_profile_list = []
        for users in username_object:
            id_profile_list.append(users.id)

        username_profile_list = []
        for id in id_profile_list:
            profile_info = Profile.objects.filter(id_user=id)
            username_profile_list.append(profile_info)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile,
                                           'username_profile_list':username_profile_list})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')

    else:
        return redirect('/')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)

    return redirect('signin')

@login_required(login_url='signin')
def profile(request, pk):
    # current user
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_count = len(user_posts)
    follower = request.user.username

    # user being looked at
    user = pk

    # if already subscribed, only unsubscribe option is given
    if FollowerCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    # info of the user being looked at
    user_followers = len(FollowerCount.objects.filter(user=pk))
    user_following = len(FollowerCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_count': user_post_count,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        # current operating user
        follower = request.POST['follower']
        # user being looked at
        user = request.POST['user']

        # delete
        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()

            return redirect('/profile' + user)

        # add
        else:
            new_follower = FollowerCount.objects.create(follower=follower, user=user)
            new_follower.save()

            return redirect('/profile' + user)

    else:
        return redirect('/')

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    # if liked by current user
    if not like_filter:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.count_of_likes += 1
        post.save()

        return redirect('/')

    # if not liked by current user
    else:
        like_filter.delete()
        post.save()

        return redirect('/')