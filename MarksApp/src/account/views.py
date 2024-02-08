from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from personal import APIToken
from .cart import Cart
from mysite.tasks import send_feedback_email_task


#email stuff
from django.core.mail import send_mail

def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = form.save()    #changed this from account = authenticate(email=email, password=raw_password) 
            login(request, account)
            return redirect('home')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'account/register.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):

    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect("home")
    
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect("home")
            
    else:
        form = AccountAuthenticationForm()
        
    context['login_form'] = form
    return render(request, 'account/login.html', context)


def account_view(request):

    if not request.user.is_authenticated:
        return redirect("login")

    # dynamically call the api to be able to check for the subjects and terms, etc.
    subjects = ["AFST", "AMST", "ANTH", "APSC", "ARAB", "ART", "ARTH", "AMES", "APIA", "BIOL", "BUAD", "CHEM", "CHIN", "CLCV",
                "COLL", "CAMS", "CSCI", "CONS", "CRWR", "CRIN", "DANC", "DATA", "ECON", "EPPL", "EDUC", "ELEM", "ENGL", "ENSP",
                "EURS", "FMST", "FREN", "GSWS", "GIS", "GEOL", "GRMN", "GOVT", "GRAD", "GREK", "HBRW", "HISP", "HIST", "INTR",
                "INRL", "ITAL", "JAPN", "KINE", "LATN", "LAS", "LAW", "LING", "MSCI", "MATH", "MLSC", "MDLL", "MUSC", "NSCI",
                "PHIL", "PHYS", "PSYC", "PBHL", "PUBP", "RELG", "RUSN", "RPSS", "SOCL", "SPCH", "THEA", "WRIT"]
    
    context = {}


    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            subject_from_post = request.POST['subject']
            term_from_post = request.POST['term']
            crn_from_post = request.POST['crn']

            form.initial = {
                "subject": subject_from_post,
                "term": term_from_post,
                "crn": crn_from_post,
            }
            failure_msg = "Class with that subject and term couldn't be found :( Please double check and try again!"
    else:
        form = AccountUpdateForm(instance=request.user)
        subject_from_post = request.user.subject
        term_from_post = request.user.term
        crn_from_post = request.user.crn
        failure_msg = "Fill in the form above to find your class!"
        
#   case for when the class no longer exists
    if term_from_post == "Summer":
        term_from_post = 202330
    elif term_from_post == "Fall":
        term_from_post = 202410
    elif term_from_post == "Spring":
        term_from_post = 202420

    APIToken.url = "https://openapi.it.wm.edu/courses/production/v1/opencourses/" + str(subject_from_post) + "/" + str(term_from_post)
    APIToken.set_headers()

    #grab the jsonData
    jsonData = APIToken.get_jsonData()

    try:
        # Check if jsonData is not None and it is not empty
        if jsonData and len(jsonData) > 0:
            # Use a regular expression pattern to clean seats available data
            pattern = r'-?\d+(?=\*)?'
            for entry in jsonData:
                if entry['CRN_ID'] == crn_from_post:
                    form.save()
                    context['success_msg'] = "Found your class! If correct, click 'Add to Cart' or search for another class!"
                    break
            else:
                # This msg is for when the class cannot be found in jsonData
                context['failure_msg'] = failure_msg
        else:
            # Handle case where jsonData is None or empty
            context['failure_msg'] = failure_msg
    except Exception as e:
        # Handle any other exceptions that might occur
        context['failure_msg'] = "An error occurred while processing your request: {}".format(str(e))


    context.update({
        'account_form': form,
        'subjects': subjects,
        'jsonData': jsonData,
        'courseURL': APIToken.url,
        'CRN': crn_from_post,
    })
    return render(request, 'account/account.html', context)

def cart_summary_view(request):
    #get the cart
    cart = Cart(request)
    cart_classes = cart.get_classes()
    return render(request, "account/cart_summary.html", {"cart_classes":cart_classes})

def cart_add_view(request):
    # get the cart
    cart = Cart(request)
    # test for post
    if request.POST.get('action') == 'post':
        # get stuff we need 
        courseURL = str(request.POST.get('courseURL'))
        CRN = str(request.POST.get('CRN'))
        TITLE = str(request.POST.get('TITLE'))

        # save to session
        cart.add(url=courseURL, CRN=CRN, title=TITLE)

        cart_quantity = cart.__len__()

        # return response
        # response = JsonResponse({'Course URL: ': courseURL, 'CRN: ': CRN})
        response = JsonResponse({'qty': cart_quantity})
        return response   


def cart_delete_view(request):
    cart = Cart(request)
    # test for post
    if request.POST.get('action') == 'post':
        # get stuff we need (only need )
        CRN = str(request.POST.get('CRN'))
        #Call delete
        cart.delete(CRN)
        response = JsonResponse({'Class CRN': CRN})
        return response   
    

def trigger_task_view(request):
    if request.POST.get('action') == 'post':
        # Extract any parameters needed for the task from the request
        email = request.user.email
        message = "test"

        # Trigger the Celery task

        #FOR SOME REASON IT DOESN"T LIKE .DELAY
        send_feedback_email_task(email, message)

        # Respond with a success message
        print("Called send_feedback_email")
        return JsonResponse({'status': 'Task triggered successfully'})
    else:
        # Return an error response if the request method is not POST or not AJAX
        return JsonResponse({'error': 'Invalid request'})







