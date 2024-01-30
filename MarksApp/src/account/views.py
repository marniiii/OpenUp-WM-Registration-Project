from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from personal import APIToken

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
                    context['failure_msg'] = "Class with that subject and term couldn't be found :( Please double check and try again!"
            #this msg is for when the jsonData DOESN'T loads and the class can't be found
            context['failure_msg'] = "Class with that subject and term couldn't be found :( Please double check and try again!"
    else:
        form = AccountUpdateForm(instance=request.user)
        subject_from_post = request.user.subject
        term_from_post = request.user.term
        crn_from_post = request.user.crn

        form.initial = {
            "subject": subject_from_post,
            "term": term_from_post,
            "crn": crn_from_post,
    }

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
        context['failure_msg'] = "Please click 'Save Changes' to check the status of your class."

    context.update({
        'account_form': form,
        'subjects': subjects,
        'jsonData': jsonData,
        'CRN': crn_from_post,
    })
    return render(request, 'account/account.html', context)






