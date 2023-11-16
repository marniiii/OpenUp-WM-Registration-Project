from django.shortcuts import render

from account.models import Account

# Create your views here.
def home_screen_view(request):

    context = {}

    subjects = ["AFST", "AMST", "ANTH", "APSC", "ARAB", "ART", "ARTH", "AMES", "APIA", "BIOL", "BUAD", "CHEM", "CHIN", "CLCV",
                "COLL", "CAMS", "CSCI", "CONS", "CRWR", "CRIN", "DANC", "DATA", "ECON", "EPPL", "EDUC", "ELEM", "ENGL", "ENSP",
                "EURS", "FMST", "FREN", "GSWS", "GIS", "GEOL", "GRMN", "GOVT", "GRAD", "GREK", "HBRW", "HISP", "HIST", "INTR",
                "INRL", "ITAL", "JAPN", "KINE", "LATN", "LAS", "LAW", "LING", "MSCI", "MATH", "MLSC", "MDLL", "MUSC", "NSCI",
                "PHIL", "PHYS", "PSYC", "PBHL", "PUBP", "RELG", "RUSN", "RPSS", "SOCL", "SPCH", "THEA", "WRIT"]
    context['subjects'] = subjects

    return render(request, "personal/home.html", context)

    # equivalent to sending this info to account/account.html