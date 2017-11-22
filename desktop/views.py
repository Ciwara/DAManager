
import json
from datetime import datetime

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
# from django.core import serializers
# from desktop.forms import LicenseForm
from desktop.models import License, Owner, Application, Host, Setup


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


# def get_app_info(request, code):

#     lcse_id, lcse = License.objects.update_or_create(code=code)
#     app = Application.objects.get(id=lcse_id)

#     data = {
#         'name': app.name,
#         'description': app.description,
#         'created_date': app.created_date
#     }
#     return JsonResponse(
#         {'message': "OK", "data": data})


def update_version(request, *args, **kwargs):
    dataset = json.loads(request.body.decode('UTF-8'))
    host_version_number = dataset.get("version_number")
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

    if last_version == host_version_number:
        last = True
    else:
        msg = "Une nouvelle version est disponible ({})".format(last_version)
    return JsonResponse({
        'setup_file_url': url, 'message': msg, "is_last": last})


@csrf_exempt
def desktop_client(request, *args, **kwargs):
    # data = {}

    # hot_id, hot = Hot.objects.update_or_create(**kwargs)
    dataset = json.loads(request.body.decode('UTF-8'))

    # {"app_info": {"name": "MPayments", "version": 1},
    #  "host_info": {"processor": "Intel64 Family 6 Model 61 Stepping 4, GenuineIntel", "version": "6.2.9200", "node": "fad", "platform": "Windows-8-6.2.9200", "system": "Windows"},
    #  "licenses": [{"code": "63c5b95438dc949a98333c8c8246da222", "isactivated": true, "activation_date": 1510210990.0, "expiration_date": 1510210990.0, "owner": "Demo", "can_expired": false},
    #               {"code": "63c5b95438dc949a98333c8c8246da22", "isactivated": true, "activation_date": 1510576371.0, "expiration_date": 1511195234.0, "owner": "Demo", "can_expired": true}]}

    licenses = dataset.get("licenses")
    host_info = dataset.get("host_info")
    app_info = dataset.get("app_info")
    # print(host_info)
    try:
        host, host_create = Host.objects.update_or_create(
            author=Owner.objects.get(username='inconnue'), defaults=host_info)
    except Exception as e:
        print("TYYYYY : ", e)
    # owner_id, owner = Owner.objects.update_or_create(**host_info)
    # print(app_info)
    app = Application.get_or_none(name=app_info.get("name"))
    if not app:
        print("Application non trouvée.")
        return JsonResponse({'status': 'Faild', 'message': '/!\ '})
    setup = Setup.objects.get(app=app, version_number=app_info.get("version"))

    print(licenses)
    for lcse in licenses:
        print("lcse", lcse)
        can_expired = lcse.get("can_expired")
        data = {
            'host': host,
            'setup': setup,
            'can_expired': can_expired,
            'isactivated': lcse.get("isactivated"),
            'activation_date': datetime.fromtimestamp(lcse.get("activation_date")),
            'expiration_date': None if not can_expired else datetime.fromtimestamp(lcse.get("expiration_date"))
        }
        # data.update({})
        msg, created = License.objects.update_or_create(
            code=lcse.get("code"), defaults=data)

    # else:
    #     owner, ok = Owner.objects.update_or_create(username=owner_name)
    #     try:
    #         l = License.objects.create(
    #             app=app, code=code_lcse, author=owner,
    #             expiration_date=expiration_date)
    #     except Exception as e:
    #         print(e)

    return JsonResponse({
        'status': 'succes', 'message': "OK"})


def dl_setup(request, setup):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/exe')
    response['Content-Disposition'] = 'attachment; filename="%s"'.format(setup)

    return response
