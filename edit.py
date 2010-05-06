#!/usr/bin/env python

from django.db import models
from reversion.revisions import revision
import subprocess
import tempfile
import time
import string
import sys
import os

from django.utils.functional import Promise

EDITOR = 'vim'

head_form = '## --%s-- %s\n'

safe_line = lambda line:[line, '\\'+line][line.startswith('## --')]
head_line = lambda line:line.startswith('## --')
back_line = lambda line:line.startswith('\\## --') and line[1:] or line
head_name = lambda line:line[len('## --'):line.find('--', len('## --'))]

def object_to_text(model, obj):
    fields = sorted((field.creation_counter, field.attname, field) for field in obj._meta.fields)
    text = ''
    for num, name, field in fields:
        text += head_form % (name, field.__class__.__name__)
        value = str(getattr(obj, name))
        if field._choices != []:
            for real,pretty in field._choices:
                if isinstance(pretty, Promise):
                    pretty = unicode(pretty)
                if value == str(real):
                    text += '+'+str(pretty)+'\n'
                else:
                    text += ' '+str(pretty)+'\n'
        else:
            value = '\n'.join(safe_line(line) for line in value.split('\n'))
            text += value + '\n'
        text += '\n'
    return text

def object_from_text(model, text):
    items = ['']
    for line in text.split('\n'):
        if head_line(line):
            items.append(line)
        else:
            items[-1] += '\n' + back_line(line)

    if items[0]:
        print 'orphaned lines. exiting'
        return False
    else:
        items = items[1:]

    dct = {}
    fdct = {}

    for field in model._meta.fields:
        fdct[field.attname] = field

    for item in items:
        head, text = item.split('\n',1)
        text = text.strip()
        if not head_line(head):
            print 'bad head: %s' % head
            return False

        name = head_name(head)
        
        field = fdct[name]
        if field._choices != []:
            value = None
            text = list(x[1:] for x in text.split('\n') if x[0]=='+')[0]
            for a,b in field.choices:
                if b == text:
                    value = a
                    break
        else:
            value = text
        if type(value)==str and value.strip() == "None" and not isinstance(field, (models.TextField, models.CharField)):
            value = None
        dct[name] = value
    return dct

def edit_object(model, object):
    revision.start()

    filename = tempfile.mktemp('.rst')
    original = object_to_text(model, object)
    open(filename, 'w').write(original)
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
            original = text
            dct = object_from_text(model, text)
            if not dct:
                open('.blogit.bad', 'w').write(text)
                print 'failed to parse'
            else:
                save_object(object, dct)

    text = open(filename).read()
    if text == original:
        return False
    dct = object_from_text(model, text)
    if not dct:
        open('.blogit.bad', 'w').write(text)
        print 'failed to parse. saved text to ".blogit.bad"'
        return False
    else:
        save_object(object, dct)
    revision.end()

def save_object(object, dct):
    for k,v in dct.iteritems():
        setattr(object, k, v)
    object.save()

# vim: et sw=4 sts=4
