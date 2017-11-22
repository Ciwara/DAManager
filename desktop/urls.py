from django.conf.urls import url

from desktop import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dashboard/(?P<pk>[-\w\d]*)$', views.dashboard, name='dashboard'),
    url(r'^desktop_client$', views.desktop_client, name='desktop-client'),
    url(r'^get_license/(?P<code>[-\w\d]*)$', views.get_license, name='add-license'),
    # url(r'^get_app_info/(?P<code>[-\w\d]*)$', views.get_app_info, name='get-info'),
    # url(r'^add_pc_info/(?P<code>[-\w\d]*)$', views.add_pc_info, name='add-pc-info'),
    url(r'^update$', views.update_version, name='update'),
    url(r'^dl/(?P<setup>[-\w\d]*)$', views.dl_setup, name='setup')
]
