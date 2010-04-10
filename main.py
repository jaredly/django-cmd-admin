#!/usr/bin/env python2.6

import tempfile
import subprocess
import string
import sys
import time
import os

sys.path.append('.')

import settings # Assumed to be in the same directory.
from django.core.management import setup_environ
setup_environ(settings)

from django.db.models.loading import cache
cache._populate()

from django.contrib import admin
admin.autodiscover()

from pick import *

from edit import totext, fromtext


from reversion.revisions import revision
import reversion

from edit import edit_object

def edit_object_old(object, field, format='rest'):
    revision.start()
    ext = {'rest':'rst','mdown':'md','txtile':'txt','html':'html','plain':'txt'}

    filename = tempfile.mktemp('.' + ext[format])
    original = getattr(object, field)
    open(filename,'w').write(original)
    mtime = os.path.getmtime(filename)

    p = subprocess.Popen((EDITOR, filename), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    while p.poll() is None:
        time.sleep(.2)
        ntime = os.path.getmtime(filename)
        if ntime > mtime:
            mtime = ntime
            text = open(filename).read()
            if text == original:
                continue
            setattr(object, field, text)
            object.save()

    text = open(filename).read()
    if text == original:
        return False
    setattr(object, field, text)
    object.save()
    revision.end()

import optparse
def get_options():
    p = optparse.OptionParser('usage: %prog [app] [model] [field]')
    p.add_option('-a', '--app', dest='app', help='django application')
    p.add_option('-m', '--model', dest='model', help='specify which model to edit')
    p.add_option('-f', '--field', dest='field', help='specify which field to edit')
    p.add_option('-n', '--num', dest='num', type='int', help='specify the object id to edit')
    p.add_option('--search', dest='search', help='search objects for "field:text"')

    options, pos = p.parse_args()
    if len(pos):
        raise Exception,'no positional arguments accepted: %s' % pos
    return options

def main():
    options = get_options()
    if not options.app:
        app = pick_app()
    else:
        app = get_app(options.app)
    if not options.model:
        model = pick_model(app)
    else:
        model = get_model(app, options.model)
    reversion.register(model)
    if options.num:
        object = get_object(model, options.num)
    elif options.search:
        object = search_object(model, options.search)
    else:
        object = pick_object(model)

    '''
    field = options.field
    if not field:
        field = pick_field(object)
    edit_object_old(object,field)
    '''
        
    edit_object(model, object)
EDITOR = 'vim'

if __name__=='__main__':
    main()

# vim: et sw=4 sts=4
