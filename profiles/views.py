from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from .models import Serviceprovider
from .models import Booking
from .models import Serviceuser as ServiceuserModel
from .forms import CreateUserForm, ServiceuserForm, BookingForm
from django.contrib import messages  # import messages
# from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm  # add this
from django.contrib.auth import authenticate, login, logout  # add this
from .models import *
from .filters import BookingFilter
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import *
# added imports
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only


# Create your views here.

# @unauthenticated_user. This works for separate register and login pages.
# @admin_only
def main(request):
	registerform = CreateUserForm()
	loginform = AuthenticationForm()
	context = {'registerform':registerform, 'loginform':loginform }

	if request.method == 'POST':
		if 'registerbtn' in request.POST:
			registerform = CreateUserForm(request.POST)
			if registerform.is_valid():
				registerform.save()
				user = registerform.cleaned_data.get('username')
				# user = registerform.save()
				# username = registerform.cleaned_data.get('username')

				# group = Group.objects.get(name='serviceuser')
				# user.groups.add()
				
				messages.success(request, 'Account was created for ' + user)
				return redirect('profiles:homepage')
			else:
				messages.error(request, "User was not created")
			loginform = AuthenticationForm(data=request.POST)
		elif 'loginbtn' in request.POST:
			loginform = AuthenticationForm(data=request.POST)
			if loginform.is_valid():
				username = loginform.cleaned_data.get('username')
				password = loginform.cleaned_data.get('password')
				user = authenticate(username=username, password=password)
				if user is not None:
					login(request, user)
					# messages.info(request, f"You are now logged in as {username}")
					return redirect('profiles:homepage')
				else:
					messages.error(request, "No user in the system yet")
			else:
				messages.error(request, "Invalid username or password.")
			loginform = AuthenticationForm()
		return render(request = request,
                    template_name = "profiles/main.html")
	return render(request, 'profiles/main.html', context)


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "profiles/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					# messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("/password_reset/done/")
					# return redirect ("profiles:homepage")

	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="profiles/password/password_reset.html", context={"password_reset_form":password_reset_form})


def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("profiles:homepage")

@login_required(login_url='profiles:homepage')
def spreg(request):
    return render(request, 'profiles/spreg.html')

# @login_required(login_url='profiles:homepage')
# def sps(request):  
#     bookings = Booking.objects.all()

#     context = {'bookings':bookings}
#     return render(request, 'profiles/sps.html',context )


@login_required(login_url='profiles:homepage')
def serviceproviderdash(request):
    # serviceproviders = ServiceProvider.objects.all()

    # context = {'serviceproviders':serviceproviders}
    return render(request, 'profiles/serviceProviderDashboard.html')


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
    bookings = Booking.objects.all()
    serviceproviders = Serviceprovider.objects.all()
    serviceusers = ServiceuserModel.objects.all()

    context = {'bookings': bookings, 'serviceproviders': serviceproviders, 'serviceusers': serviceusers}
    return render(request, 'profiles/dashboard.html', context)


@login_required(login_url='profiles:homepage')
def createbBooking(request):

    serviceusers = ServiceuserModel.objects.all()
	# serviceproviders = Serviceprovider.objects.all()
	# bookings = Booking.objects.all()
	

    bookingform = BookingForm()
    if request.method == 'POST':
        # print('Printing post:', request.POST)
        bookingform = BookingForm(request.POST)
        if bookingform.is_valid():
            bookingform.save()
            return redirect(reverse ('profiles:serviceuserdash'))

    context = {'bookingform': bookingform, serviceusers: serviceusers}
	# 	context = {'form': form, serviceusers: serviceusers, serviceproviders: serviceproviders, bookings: bookings}
    return render(request,'profiles/bookingform.html', context)
	# return render(request, template_name='profiles/bookingform.html', context)


@login_required(login_url='profiles:homepage')
def serviceuserdash(request):
    return render(request, 'profiles/serviceuserdash.html')


def serviceuser(request):

    serviceusers = ServiceuserModel.objects.all()

    form = ServiceuserForm()
    if request.method == 'POST':
        # print('Printing post:', request.POST)
        form = ServiceuserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse ('profiles:dashboard'))

    context = {'form': form, serviceusers: serviceusers}
    return render(request,'profiles/serviceuser.html', context)


@login_required(login_url='profiles:homepage')
def updateServiceuser(request, pk):

    serviceusers = ServiceuserModel.objects.get(id=pk)
    form = ServiceuserForm(instance=serviceusers)

    if request.method == 'POST':
        form = ServiceuserForm(request.POST, instance=serviceusers)
        if form.is_valid():
            form.save()
            return redirect(reverse ('profiles:dashboard'))

    context = {'form': form}
    return render(request, 'profiles/serviceuser.html', context) 


@login_required(login_url='profiles:homepage')
def deleteServiceuser(request, pk):
    serviceusers = ServiceuserModel.objects.get(id=pk)
    if request.method == "POST":
        serviceusers.delete()
        return redirect(reverse ('profiles:dashboard'))
    context = {'item': serviceusers}
    return render(request, 'profiles/deleteServiceuser.html', context) 


@login_required(login_url='profiles:homepage')
# @allowed_users(allowed_roles=['serviceuser'])
def userPage(request):
	bookings = request.user.serviceuser.order_set.all()
	context = {}
	return render(request, 'profiles/user.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def captioningList(request):
	return render(request, 'profiles/splist/captioning.html')


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def internationalInterpList(request):
	return render(request, 'profiles/splist/internationalInterp.html')


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def mobGuideList(request):
	return render(request, 'profiles/splist/mobGuide.html')


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def personalSupportList(request):
	return render(request, 'profiles/splist/personalSupport.html')


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def ugandanInterpList(request):
	return render(request, 'profiles/splist/ugandaInterpreter.html')