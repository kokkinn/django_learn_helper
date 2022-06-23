from django.shortcuts import render


words = [
    {"id": 1, "en": "beget", "rus": "порождать"},
    {"id": 2, "en": "learn", "rus": "учить"},
    {"id": 3, "en": "hide", "rus": "прятаться"},
]


def home_view(request):
    return render(request, "words/home.html")


def list_view(request, pk):
    context = {"words": words}
    return render(request, "words/list.html", context)


def add_view(request):
    return render(request, "words/add.html")


def test_view(request):
    return render(request, "words/test.html")
