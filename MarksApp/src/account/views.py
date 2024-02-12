# import all the things needed
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from .cart import Cart

#using tasks and celery here to getJsonData
from mysite import tasks

#using this to send emails
from mysite.tasks import send_feedback_email_task

# make a register view
def registration_view(request):
    context = {}
    # if info sent to this view is post
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


# send user back to the home screen
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

    # this only needs to be called every week or so
    tasks.url = "https://openapi.it.wm.edu/courses/production/v1/subjectlist"
    tasks.set_headers()

    # use .delay on this command below once i figure out why .delay breaks it
    subjects = tasks.get_jsonData()
    subject_list = []
    for entry in subjects:
        # Use .get() method to access the 'STVSUBJ_CODE' key with a default value of None
        subject_code = entry.get('STVSUBJ_CODE')
        if subject_code is not None:
            subject_list.append(subject_code)

        subject_list.sort()

        context = {}

    
    # if get a post request from account searching for a class
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
    # if it fails or it's their first time visiting the account page
    else:
        form = AccountUpdateForm(instance=request.user)
        # use their old saved info and display it
        subject_from_post = request.user.subject
        term_from_post = request.user.term
        crn_from_post = request.user.crn
        failure_msg = "Fill in the form above to find your class!"
        
    #  this also only needs to be called like once a week or more rarely
    #  also make it so that only terms with add drop active are displayed
    # call api to get the actual active term codes and see if it matches the input
    tasks.url = "https://openapi.it.wm.edu/courses/production/v1/activeterms"
    tasks.set_headers()
    terms = tasks.get_jsonData()

    for entry in terms:
        # if user selects summer, fall, or spring, see if that's something that thte api returns
        if term_from_post in entry['TERM_DESC']:
            # if so, set term_from_post = to the numerical value of that term
            term_from_post = entry['TERM_CODE']
            break
        # otherwise just set it to 0 so that the failure msg will pop up
        else:
            term_from_post = 0
            
    # set the tasks.url to the url used to grab class jsonData
    tasks.url = "https://openapi.it.wm.edu/courses/production/v1/opencourses/" + str(subject_from_post) + "/" + str(term_from_post)
    # do some stuff
    tasks.set_headers()

    #DOESN"T LIKE jsonData = tasks.get_jsonData.delay() or tasks.get_jsonData.delay().get()
    #tasks.get_jsonData.delay().get()
    #grab the jsonData using tasks and celery
    jsonData = tasks.get_jsonData()

    try:
        # Check if jsonData is not None and it is not empty
        if jsonData and len(jsonData) > 0:
            # Use a regular expression pattern to clean seats available data
            pattern = r'-?\d+(?=\*)?'
            # for every entry in that huge jsonData
            for entry in jsonData:
                # if we find a match regarding CRN
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

    # then we want to send the form, subjects, jsonData, url, and the crn to account.html so that it can use it or display it
    context.update({
        'account_form': form,
        'subjects': subject_list,
        'jsonData': jsonData,
        'courseURL': tasks.url,
        'CRN': crn_from_post,
    })
    # this sends that info there
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
        send_feedback_email_task.delay(email, message)

        # Respond with a success message
        print("Called send_feedback_email")
        return JsonResponse({'status': 'Task triggered successfully'})
    else:
        # Return an error response if the request method is not POST or not AJAX
        return JsonResponse({'error': 'Invalid request'})







