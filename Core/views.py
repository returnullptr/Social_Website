from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages

# Create your views here.

#
def signup(request):
    return

#
def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # verify
        user = auth.authenticate(username=username, password=password)

        # if user exists
        if user is not None:
            messages.info(request, "Successfully Logged In")
            return redirect('signin')
        # if user does not exist
        else:
            messages.info(request, "Unable to Log In")
            return redirect('signin')

    else:
        return render(request, 'signin.html')

def signup(request):
    if request.method == "POST":
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
                messages.info(request, "Successfully Signed Up")
                return redirect('signup')

        else:
            messages.info(request, "Passwords Do Not Match")
            return redirect('signup')

    else:
        return render(request, 'signup.html')


#
def settings(request):
    if request.method == "POST":
        return redirect(settings)

    else:
        return render(request, 'settings.html')