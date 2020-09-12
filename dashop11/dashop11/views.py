from django.http import HttpResponse


def test_cors(request):
    # test cors.
    return HttpResponse('--hahahahhaha--')