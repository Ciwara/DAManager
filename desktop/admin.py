# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from django.contrib import admin
# from django.db import models

# from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from desktop.forms import (UserChangeForm, UserCreationForm)
from desktop.models import (Member, License, Owner, Application, Setup)

# unregister and register again
# admin.site.unregister(Group)


@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):

    model = Setup

    list_filter = ['app']


class SetupInline(admin.TabularInline):

    model = Setup
    extra = 0


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):

    model = Owner


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    model = Application

    inlines = [
        SetupInline,
    ]


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):

    model = License
    list_filter = ['isactivated', 'author']


@admin.register(Member)
class MemberAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'email', 'date_of_birth', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
                                      'date_of_birth', 'email',)}),
        # ('Permissions', {'fields': ('groups', 'is_admin')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide', 'extrapretty'),
                'fields': ('username', 'password1', 'password2', )}),
        ('Personal info', {'fields': ('first_name', 'image', 'last_name',
                                      'date_of_birth', 'email')}),
        # ('Permissions', {'fields': ('groups', 'is_admin')}),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
