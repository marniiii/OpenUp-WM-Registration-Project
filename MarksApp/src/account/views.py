# import all the things needed
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from .cart import Cart
from .models import WatchedClass

#using tasks and celery here to getJsonData
from mysite import tasks

#using this to send emails
from mysite.tasks import send_feedback_email_task

# trying to persist cart after logout


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
    
    context = {}

    # this only needs to be called every week or so
    # set the subject_url and term_url to visit that site and grab
    subject_url = "https://openapi.it.wm.edu/courses/production/v1/subjectlist"
    term_url = "https://openapi.it.wm.edu/courses/production/v1/activeterms"

    # call the function and set subjects and term = to the celery task response
    # subjects, terms = tasks.get_subject_and_term.delay(subject_url, term_url).get()

    subject_list = []
    # for entry in subjects:
    #     # Use .get() method to access the 'STVSUBJ_CODE' key with a default value of None
    #     subject_code = entry.get('STVSUBJ_CODE')
    #     if subject_code is not None:
    #         subject_list.append(subject_code)

    #     # this is how we get the sorted subjects for the dropdown menu
    #     subject_list.sort()


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


    #  also make it so that only terms with add drop active are displayed
    # for entry in terms:
    #     # if user selects summer, fall, or spring, see if that's something that the api returns
    #     if str(term_from_post) in entry['TERM_DESC']:
    #         # if so, set term_from_post = to the numerical value of that term
    #         term_from_post = entry['TERM_CODE']
    #         break
    #     # otherwise just set it to 0 so that the failure msg will pop up
    #     else:
    #         term_from_post = 0


    # set the tasks.url to the url used to grab class jsonData
    # classes_url = "https://openapi.it.wm.edu/courses/production/v1/opencourses/" + str(subject_from_post) + "/" + str(term_from_post)

    # #grab the jsonData using tasks and celery
    # classesJsonData = tasks.get_classes.delay(classes_url).get()
    

    # try:
    #     # Check if jsonData is not None and it is not empty
    #     if classesJsonData and len(classesJsonData) > 0:
    #         # Use a regular expression pattern to clean seats available data
    #         pattern = r'-?\d+(?=\*)?'
    #         # for every entry in that huge jsonData
    #         for entry in classesJsonData:
    #             # if we find a match regarding CRN
    #             if entry['CRN_ID'] == crn_from_post:
    #                 form.save()
    #                 context['success_msg'] = "Found your class! If correct, click 'Add to Cart' or search for another class!"
    #                 break
    #         else:
    #             # This msg is for when the class cannot be found in jsonData
    #             context['failure_msg'] = failure_msg
    #     else:
    #         # Handle case where jsonData is None or empty
    #         context['failure_msg'] = failure_msg
    # except Exception as e:
    #     # Handle any other exceptions that might occur
    #     context['failure_msg'] = "An error occurred while processing your request: {}".format(str(e))

    # # then we want to send the form, subjects, jsonData, url, and the crn to account.html so that it can use it or display it
    # context.update({
    #     'account_form': form,
    #     'subjects': subject_list,
    #     'jsonData': classesJsonData,
    #     'courseURL': classes_url,
    #     'CRN': crn_from_post,
    # })
    # # this sends that info there
    return render(request, 'account/account.html', context)


def cart_summary_view(request):
    user = request.user
    if user.is_authenticated:
        cart_classes = WatchedClass.objects.filter(account=user)

    print(cart_classes)
    
    return render(request, "account/cart_summary.html", {"cart_classes":cart_classes})

    #get the cart
    # cart = Cart(request)
    # cart_classes = cart.get_classes()
    # return render(request, "account/cart_summary.html", {"cart_classes":cart_classes})


def cart_add_view(request):
    # # get the cart
    # cart = Cart(request)
    # # test for post
    # if request.POST.get('action') == 'post':
    #     # get stuff we need 
    #     courseURL = str(request.POST.get('courseURL'))
    #     CRN = str(request.POST.get('CRN'))
    #     TITLE = str(request.POST.get('TITLE'))

    #     # save to session
    #     cart.add(url=courseURL, CRN=CRN, title=TITLE)

    #     cart_quantity = cart.__len__()

    #     # return response
    #     # response = JsonResponse({'Course URL: ': courseURL, 'CRN: ': CRN})
    #     response = JsonResponse({'qty': cart_quantity})
    #     return response   

    # test for post
    if request.POST.get('action') == 'post':
        # get stuff we need 
        courseURL = str(request.POST.get('courseURL'))
        CRN = str(request.POST.get('CRN'))
        TITLE = str(request.POST.get('TITLE'))
        user = request.user


        # Check if a WatchedClass object with the given CRN already exists
        existing_watched_class = WatchedClass.objects.filter(crn=CRN, account=user).first()
        if existing_watched_class:
            # Return an error message if a WatchedClass with the same CRN exists
            return JsonResponse({'success': False, 'message': 'A watched class with the same CRN already exists.'}, status=400)
    
    # If no existing WatchedClass with the same CRN, create a new one
        watched_class = WatchedClass.objects.create(
            crn=CRN,
            url=courseURL,
            title=TITLE,
            account=user
        )

        # return response
        return JsonResponse({'success': True})


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







