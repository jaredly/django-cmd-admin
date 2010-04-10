#!/usr/bin/env python
from django.db.models.loading import cache
from utils import *

def pick_app():
    app = pick(enumerate(cache.app_models.keys()))
    if not app:
        sys.exit(0)
    return app

def get_app(app):
    if app not in cache.app_models:
        print 'Invalid app'
        return pick_app()
    return cache.app_models[app]

def pick_model(app):
    model = pick(enumerate(app.keys()))
    if not model:
        sys.exit(0)
    return app[model]

def get_model(app, model):
    if not model in app:
        print 'Invalid model'
        return pick_model(app)
    return app[model]

def get_object(model, pk):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        return pick_object(model)

def pick_object(model):
    obj = pick_table((obj,[i]+strobj(obj, model)) for i, obj in enumerate(model.objects.all()))
    if not obj:
        sys.exit(0)
    return obj

def search_object(model, text):
    try:
        field, kwds = text.split(':', 1)
        return model.objects.get(**{field+'__contains':kwds})
    except model.MultipleObjectsReturned:
        print 'search is not specific enough'
    except model.DoesNotExist:
        print 'no objects found'
    return pick_object(model)

def pick_field(object):
    field = pick(enumerate(vars(object).keys()))
    if not field:
        sys.exit(0)
    return field


# vim: et sw=4 sts=4
