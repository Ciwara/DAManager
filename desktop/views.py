
import json
from datetime import datetime

from django.shortcuts import render
# from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponse
# from django.core import serializers
# from desktop.forms import LicenseForm
from desktop.models import License, Owner, Application, Hot, Setup


def index(request, *args, **kwargs):
    apps = Application.objects.all()
    return render(request, 'index.html', {"apps": apps})


def dashboard(request, *args, **kwargs):
    apps = Application.objects.all()
    return render(request, 'dashboard.html', {"apps": apps})


def get_license(request, code):

    lcse = License.objects.get(code=code)

    data = {
        'author': lcse.author, 'app': lcse.app,
        'can_expired': lcse.can_expired,
        'isactivated': lcse.isactivated,
        'activation_date': lcse.activation_date,
        'expiration_date': lcse.expiration_date
    }
    return JsonResponse(
        {'message': "OK", "data": data})


def get_app_info(request, code):

    lcse_id, lcse = License.objects.update_or_create(code=code)
    app = Application.objects.get(id=lcse_id)

    data = {
        'name': app.name,
        'description': app.description,
        'created_date': app.created_date
    }
    return JsonResponse(
        {'message': "OK", "data": data})


def update_version(request, *args, **kwargs):
    dataset = json.loads(request.body.decode('UTF-8'))
    hot_version_number = dataset.get("version_number")
    app_name = dataset.get("app_name")
    msg = "OK"
    last = False
    try:
        app = Application.objects.get(name=app_name)
    except Exception as e:
        print(e)
        return
    last_setup = app.last_setup
    url = last_setup.file.url
    last_version = last_setup.version_number

    if last_version == hot_version_number:
        last = True
    else:
        msg = "Une nouvelle version est disponible ({})".format(last_version)
    return JsonResponse({
        'setup_file_url': url, 'message': msg, "is_last": last})


def add_pc_info(request, *args, **kwargs):
    hot_id, hot = Hot.objects.update_or_create(**kwargs)

    return JsonResponse(
        {'message': "OK", "message": hot})


# @csrf_protect
def add_license(request, *args, **kwargs):
    # data = {}
    # dataset = request.body
    dataset = json.loads(request.body.decode('UTF-8'))
    license = dataset.get("license")
    owner_name = license.get("owner")
    app_name = license.get("app_name")
    code_lcse = license.get("code")
    can_expired = license.get("can_expired")
    expiration_date = None if not can_expired else datetime.fromtimestamp(
        license.get("expiration_date"))
    print(license)
    app = Application.get_or_none(name=app_name)
    if not app:
        print("Application non trouvée.")
        return JsonResponse({'status': 'Faild', 'message': '/!\ '})
    else:
        owner, ok = Owner.objects.update_or_create(username=owner_name)
        try:
            l = License.objects.create(
                app=app, code=code_lcse, author=owner,
                expiration_date=expiration_date)
        except Exception as e:
            print(e)

    return JsonResponse({
        'status': 'succes', 'message': "OK"})


def dl_setup(request, setup):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/exe')
    response['Content-Disposition'] = 'attachment; filename="%s"'.format(setup)

    return response
