#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json
import os
import re
import requests
import six
import textwrap

from jinja2 import Environment, FileSystemLoader


def load_json(url):
    # TODO retries
    r = requests.get(url, timeout=10)
    # TODO error checking
    return r.json()
#    # i think we can replace this with a url requests json
#    data = open(filename).read()
#    # this is requests?
#    # START We don't need this code if we're reading from the api
#    # Strip out leading 'module.exports = {'
#    lines = data.split('\n')
#    lines[0] = '{'
#    # And trailing };
#    lines[-1] = '}'
#    data = ''.join(lines)
#    # END
#    return json.loads(data)


def argumentstring(entry):
    '''
    Returns an argument string for the given function
    '''
    argument_names = ['self']
    argument_names.extend(entry['args'])
    if 'input' in entry:
        input_name = 'payload'
        argument_names.append(input_name)
    return ", ".join(argument_names)


def angles_to_braces(s):
    '''
    Returns a string with <vars> replaced by {vars}
    '''
    return re.sub('<(.*?)>', '{\\1}', s)


def render(env, template_name, api, service_name, url):
    template = env.get_template(template_name)
    return template.render(
        service_name=service_name,
        api=api,
        argumentstring=argumentstring,
        reference_url = url,
    )


def stringify(s):
    # TODO
    return s


def docstringify(s, level=4):
    lines = []
    wrapper = textwrap.TextWrapper(subsequent_indent=' ' * level,
                                   expand_tabs=True, width=100)
    for line in s.splitlines():
        lines.extend(wrapper.wrap(line))
        wrapper.initial_indent = ' ' * level

    return '\n'.join(lines)


def to_unicode(obj):
    try:
        obj = obj.encode('utf-8')
    except TypeError:
        pass
    return obj


if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['string'] = stringify
    env.filters['docstring'] = docstringify
    env.filters['angles_to_braces'] = angles_to_braces
    # nuke + create tc/
    # touch tc/__init__.py
    # go through original json
    key = 'Queue'
    name = key.lower()
    url = 'http://references.taskcluster.net/queue/v1/api.json'
    api = load_json(url)
    code = render(env, 'queue.py.template', api, key, url)
    with open(os.path.join(os.getcwd(), 'tc', '{}.py'.format(name)),
              'w') as fh:
        code = to_unicode(code)
        print(code, file=fh)
