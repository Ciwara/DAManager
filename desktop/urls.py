from django.conf.urls import url

from desktop import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^license$', views.add_license, name='add-license'),
    url(r'^get_license/(?P<code>[-\w\d]*)$',
        views.add_license, name='add-license'),
    url(r'^get_app_info/(?P<code>[-\w\d]*)$',
        views.get_app_info, name='get-info'),
    url(r'^add_pc_info/(?P<code>[-\w\d]*)$',
        views.add_pc_info, name='add-pc-info'),
    url(r'^update$', views.update_version, name='update')
]
