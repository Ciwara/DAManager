
import json
from datetime import datetime

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from desktop.models import License, Organization, Application, Host, Setup


def index(request, *args, **kwargs):
    apps = {}
    for app in Application.objects.all():
        list_setup = []
        for setup in Setup.objects.filter(app=app, active=True):
            setup.url_display = reverse("dl_setup", args=[setup.id])
            list_setup.append(setup)
        apps.update({app: list_setup})

    return render(request, 'index.html', {"apps": apps})


def dashboard(request, *args, **kwargs):
    apps = Application.objects.all()
    return render(request, 'dashboard.html', {"apps": apps})


@csrf_exempt
def desktop_client(request, *args, **kwargs):

    dataset = json.loads(request.body.decode('UTF-8'))
    msg = "OK"
    licenses = dataset.get("licenses")
    host_info = dataset.get("host_info")
    app_info = dataset.get("app_info")
    host_version = app_info.get("version")
    app_name = app_info.get("name")
    organization = dataset.get("organization")

    organ, organ_create = Organization.objects.update_or_create(
        member=None, defaults=organization)
    host, host_create = Host.objects.update_or_create(
        organization=organ, defaults=host_info)
    print(app_info)
    app = Application.get_or_none(name=app_name)
    if not app:
        print("Application non trouvée.")
        return JsonResponse({'status': 'Faild', 'message': '/!\ '})
    last_setup = app.last_setup
    url = last_setup.file.url
    last_version = last_setup.version_number
    host_setup = Setup.objects.get(app=app, version_number=host_version)
    if int(last_version) == int(host_setup.version_number):
        last = True
    else:
        last = False
        msg = "La version {} est disponible.".format(last_version)

    for lcse in licenses:
        print("lcse", lcse)
        can_expired = lcse.get("can_expired")
        data = {
            "host": host,
            "setup": host_setup,
            "can_expired": can_expired,
            "isactivated": lcse.get("isactivated"),
            "activation_date": datetime.fromtimestamp(
                lcse.get("activation_date")),
            "expiration_date": None if not can_expired else datetime.fromtimestamp(lcse.get("expiration_date"))
        }
        # data.update({})
        lcse, created = License.objects.update_or_create(
            code=lcse.get("code"), defaults=data)
        is_kill = lcse.is_kill
    # TODO
    return JsonResponse({
        "setup_file_url": url, "message": msg, "is_last": last,
        "version": last_version, "is_kill": is_kill})


def dl_setup(request, *args, **kwargs):
    print(kwargs)
    setup_id = kwargs["setup_id"]
    setup = Setup.objects.get(id=setup_id)
    setup.nb_download += 1
    setup.save()
    redirect("/")
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/exe')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        setup.file)

    return response
