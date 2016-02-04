#!/usr/bin/env python
import re
import json
import textwrap

from jinja2 import Environment, FileSystemLoader


def load_apis(filename):
    data = open(filename).read()
    # Strip out leading 'module.exports = {'
    lines = data.split('\n')
    lines[0] = '{'
    # And trailing };
    lines[-1] = '}'
    data = ''.join(lines)
    return json.loads(data)


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


def render(env, template_name, apis, service_name):
    template = env.get_template(template_name)
    return template.render(
        service_name=service_name,
        apis=apis,
        api=apis[service_name],
        argumentstring=argumentstring,
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


if __name__ == '__main__':
    env = Environment(loader=FileSystemLoader('templates'))
    env.filters['string'] = stringify
    env.filters['docstring'] = docstringify
    env.filters['angles_to_braces'] = angles_to_braces
    apis = load_apis('apis.js')
    queue_code = render(env, 'queue.py.template', apis, 'Queue')
    print(queue_code)
