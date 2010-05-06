#!/usr/bin/env python

from django.contrib import admin

def strobj(obj, model):
    if model not in admin.site._registry:
        return [str(obj)]
    amod = admin.site._registry[model]
    if not amod.list_display:
        return [str(obj)]
    return list(str(getattr(obj, attr)) for attr in amod.list_display if hasattr(obj, attr))

def pick_table(lst, new=False):
    lst = list(lst)
    mx_lens = []
    for i in range(0, len(lst[0][1])):
        mx_lens.append(0)
        for obj, line in lst:
            if len(str(line[i])) > mx_lens[i]:
                mx_lens[i] = len(str(line[i]))
    dct = {}
    for obj, line in lst:
        dct[str(line[0])] = obj
        st = str(line[0]).ljust(mx_lens[0])
        st += ') ' + ' '.join(str(line[i]).ljust(mx_lens[i]) for i in range(1, len(line)))
        print st

    while True:
        inp = raw_input('pick one: ')
        if inp in dct:
            return dct[inp]
        elif not inp:
            return None

def pick(lst, name=None, flat=True):
    dct = {}
    for i,item in lst:
        dct[str(i)] = item
        if not flat:
            print '%s) %s' % (i, item[1])
        else:
            print '%s) %s' % (i, item)
    while True:
        inp = raw_input('pick one: ')
        if inp in dct:
            if not flat:
                return dct[inp][0]
            return dct[inp]
        elif not inp:
            return None

# vim: et sw=4 sts=4
