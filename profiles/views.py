from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import Serviceuser as ServiceuserModel, Booking, Serviceprovider
from .forms import CreateUserForm, ServiceuserForm, BookingForm
from django.contrib import messages  # import messages
# from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm  # add this
from django.contrib.auth import authenticate, login, logout  # add this
from .filters import BookingFilter
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import *
# added imports
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only



# Create your views here.

# @unauthenticated_user. This works for separate register and login pages.
def main(request):
	registerform = CreateUserForm()
	loginform = AuthenticationForm()
	context = {'registerform':registerform, 'loginform':loginform }

	if request.method == 'POST':
		if 'registerbtn' in request.POST:
			registerform = CreateUserForm(request.POST)
			if registerform.is_valid():
				user = registerform.save()
				username = registerform.cleaned_data.get('username')
				messages.success(request, 'Account was created for ' + username)
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
					messages.info(request, f"You are now logged in as {username}")
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


@login_required(login_url='profiles:homepage')
# @allowed_users(allowed_roles=['serviceprovider'])
def serviceproviderdash(request):
	bookings = request.user.serviceprovider.booking_set.all()
	
	context = {'bookings': bookings }
	return render(request, 'profiles/serviceProviderDashboard.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['admin'])
def dashboard(request):
	bookings = Booking.objects.all()
	serviceproviders = Serviceprovider.objects.all()
	serviceusers = ServiceuserModel.objects.all()

	total_bookings = bookings.count()
	total_serviceproviders = serviceproviders.count()
	total_serviceusers = serviceusers.count()

	# ongoing = bookings.filter(status='Ongoing').count()
	# completed = bookings.filter(status='Completed').count()
	# cancelled = bookings.filter(status='Cancelled').count()

	context = {'bookings': bookings, 'serviceproviders': serviceproviders, 'serviceusers': serviceusers}
	return render(request, 'profiles/dashboard.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def createbBooking(request, pk):
	serviceusers = ServiceuserModel.objects.all()
	serviceprovider = Serviceprovider.objects.get(id=pk)
	bookingform = BookingForm()
	
	if request.method == 'POST':
		print('Printing post:', request.POST)
		bookingform = BookingForm(request.POST)
		
		if bookingform.is_valid():
			bookingform.save()
			return redirect(reverse ('profiles:serviceuserdash'))

	context = {'bookingform': bookingform, 'serviceprovider':serviceprovider, 'serviceusers':serviceusers}
	return render(request,'profiles/bookingform.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser'])
def serviceuserdash(request):
	bookings = request.user.serviceuser.booking_set.all()
	
	# for booking in bookings:
	# 	booking.service_hours = (int(float(booking.endtime)) - int(float(booking.starttime)))
	total_bookings = bookings.count()
	# ongoing = bookings.filter(status='Ongoing').count()
	# completed = bookings.filter(status='Completed').count()
	# cancelled = bookings.filter(status='Cancelled').count()

	# context = {'bookings': bookings, 'total_bookings': total_bookings, 'ongoing': ongoing, 'completed': completed, 'cancelled': cancelled,}
	context = {'bookings': bookings}
	return render(request, 'profiles/serviceuserdash.html', context)


# @login_required(login_url='profiles:homepage')
# @allowed_users(allowed_roles=['serviceuser'])
# def addServiceuser(request):
# 	serviceusers = ServiceuserModel.objects.all()
# 	user = request.user
# 	form = ServiceuserForm(instance=user)
# 	if request.method == 'POST':
# 		form = ServiceuserForm(request.POST, request.FILES, instance=user)
# 		if form.is_valid():
# 			form.save()
# 			return redirect(reverse ('profiles:homepage'))
# 	else:
# 		context = {'form': form, serviceusers: serviceusers}
# 	return render(request,'profiles/addServiceuser.html', context)

@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser'])
def serviceUserProfile(request):
	serviceuser = request.user.serviceuser
	username = request.user
	firstname = serviceuser.firstname
	lastname = serviceuser.lastname
	phone = serviceuser.phone
	email = serviceuser.email
	date = serviceuser.date_created
	profile_pic = serviceuser.profile_pic

	context = {'username':username, 'firstname':firstname, 'lastname':lastname, 'phone':phone, 'email':email, 'date':date, }
	return render(request, 'profiles/serviceuserProfile.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def updateServiceuser(request, pk):
    serviceusers = ServiceuserModel.objects.get(id=pk)
    form = ServiceuserForm(instance=serviceusers)

    if request.method == 'POST':
        form = ServiceuserForm(request.POST, request.FILES, instance=serviceusers)
        if form.is_valid():
            form.save()
            return redirect(reverse ('profiles:profile'))

    context = {'form': form}
    return render(request, 'profiles/editServiceuser.html', context) 


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['admin'])
def deleteServiceuser(request, pk):
    serviceusers = ServiceuserModel.objects.get(id=pk)
    if request.method == "POST":
        serviceusers.delete()
        return redirect(reverse ('profiles:dashboard'))
    context = {'item': serviceusers}
    return render(request, 'profiles/deleteServiceuser.html', context) 

@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser'])
def serviceProviderProfile(request):
	serviceprovider = request.user.serviceprovider
	username = request.user
	fullname = serviceprovider.fullname
	gender = serviceprovider.gender
	phone = serviceprovider.phone
	email = serviceprovider.email
	address = serviceprovider.phyadd
	service = serviceprovider.service

	context = {'username':username, 'fullname':fullname, 'gender':gender, 'phone':phone, 'email':email, 'address':address, 'service':service}
	return render(request, 'profiles/serviceproviderProfile.html', context)

# @login_required(login_url='profiles:homepage')
# @allowed_users(allowed_roles=['serviceprovider', 'admin'])
# def updateServiceprovider(request, pk):
#     serviceprovider = Serviceprovider.objects.get(id=pk)
#     form = ServiceproviderForm(instance=serviceprovider)

#     if request.method == 'POST':
#         form = ServiceproviderForm(request.POST, request.FILES, instance=serviceprovider)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse ('profiles:profile'))

#     context = {'form': form}
#     return render(request, 'profiles/editServiceprovider.html', context) 

@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def captioningList(request):
	serviceproviders = Serviceprovider.objects.all()
	context = {'serviceproviders': serviceproviders}
	return render(request, 'profiles/splist/captioning.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def internationalInterpList(request):
	serviceproviders = Serviceprovider.objects.all()
	context = {'serviceproviders': serviceproviders}
	return render(request, 'profiles/splist/internationalInterp.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def mobGuideList(request):
	serviceproviders = Serviceprovider.objects.all()
	context = {'serviceproviders': serviceproviders}
	return render(request, 'profiles/splist/mobGuide.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def personalSupportList(request):
	serviceproviders = Serviceprovider.objects.all()
	context = {'serviceproviders': serviceproviders}
	return render(request, 'profiles/splist/personalSupport.html', context)


@login_required(login_url='profiles:homepage')
@allowed_users(allowed_roles=['serviceuser', 'admin'])
def ugandanInterpList(request):
	serviceproviders = Serviceprovider.objects.all()
	context = {'serviceproviders': serviceproviders}
	return render(request, 'profiles/splist/ugandaInterpreter.html', context)


@login_required(login_url='profiles:homepage')
# @admin_only
def generalDash(request):
	return render(request, 'profiles/generalDashboard.html')


# @login_required(login_url='profiles:homepage')
# @allowed_users(allowed_roles=['serviceuser', 'admin'])
def spList(request):
	serviceproviders = Serviceprovider.objects.all()
	context = {'serviceproviders': serviceproviders}
	return render(request, 'profiles/splist/allServiceProviders.html', context)


# @login_required(login_url='profiles:homepage')
# @allowed_users(allowed_roles=['serviceuser', 'admin'])
# def pickServiceuser(request, pk):
# 	serviceproviders = Serviceprovider.objects.get(id=pk)
# 	# form = ServiceuserForm(instance=serviceusers)

# 	# if request.method == 'POST':
# 	#     form = ServiceuserForm(request.POST, instance=serviceusers)
# 	#     if form.is_valid():
# 	#         form.save()
# 	#         return redirect(reverse ('profiles:serviceuserdash'))

# 	# context = {'form': form}
# 	context = {}
# 	return render(request, 'profiles/bookingform.html', context) 
