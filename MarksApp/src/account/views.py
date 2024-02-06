from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from personal import APIToken
from .cart import Cart


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

#           case for when the class no longer exists
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
            #use this pattern to get rid of weird symbols in seats avai
            pattern = r'-?\d+(?=\*)?'
            for entry in jsonData:
                if entry['CRN_ID'] == crn_from_post:
                    form.save()
                    context['success_msg'] = "Found your class! If correct, click 'Add to Cart' or search for another class!"
                    #START THREAD HERE
                    break
                else:
                    #this msg is for when the jsonData loads, but the class can't be found
                    context['failure_msg'] = "Class with that subject and term couldn't be found :( Please double check and try again!"
            #this msg is for when the jsonData DOESN'T loads and the class can't be found
            context['failure_msg'] = "Class with that subject and term couldn't be found :( Please double check and try again!"
    else:
        form = AccountUpdateForm(instance=request.user)
        subject_from_post = request.user.subject
        term_from_post = request.user.term
        crn_from_post = request.user.crn

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
        #use this pattern to get rid of weird symbols in seats avai
        pattern = r'-?\d+(?=\*)?'

        for entry in jsonData:
            if entry['CRN_ID'] == crn_from_post:
                form.save()
                context['success_msg'] = "Found your class. On your watchlist!"
                break
            else:
                #this msg is for when the jsonData loads, but the class can't be found
                context['failure_msg'] = "ENTERED ELSE"
                break
        #this msg is for when the jsonData DOESN'T loads and the class can't be found
        context['failure_msg'] = "Please select a Subject, Term, and CRN you'd like to watch"

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


def cart_update_view(request):
    pass







