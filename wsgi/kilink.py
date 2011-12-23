#!/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Facundo Batista, Nicolás César
# All Rigths Reserved

"""Kilink FTW!"""

import os
import sys

from flup.server.fcgi import WSGIServer
from mako.template import Template

import backend
import tools

FCGI_SOCKET_DIR = '/tmp'
FCGI_SOCKET_UMASK = 0111

MAIN_PAGE = Template(file('templates/index.html').read())

klnkbkend = backend.KilinkBackend()


def kilink(environ, start_response, extra_data={}):
    """Kilink, :)"""
    path_info = environ['PATH_INFO']
    query_string = environ['QUERY_STRING']
    render_dict={'value':''}
    render_dict.update(extra_data)

    if path_info == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [str(MAIN_PAGE.render(**render_dict))]

    if path_info == '/action/create':
        response = str(environ)
        post_data = environ['wsgi.input'].read()
        assert post_data[:8] == 'content='
        print "======== raw", repr(post_data[8:])
        content = tools.magic_quote(post_data[8:])
        print "======== cnt", repr(content)
        kid = klnkbkend.create_kilink(content)
        start_response('303 see other', [('Location', "/" + kid)])
        return ''

    # serving a kilink
    start_response('200 OK', [('Content-Type', 'text/html')])
    kid = path_info[1:]
    response = klnkbkend.get_content(kid, 1)
    render_dict.update({'value': response})
    return [MAIN_PAGE.render(**render_dict)]


def main(args_in, app_name="hello"):
    """Go girl."""
    socketfile = os.path.join(FCGI_SOCKET_DIR, 'kilink.socket' )

    try:
        srvr = WSGIServer(kilink, bindAddress=socketfile,
                          umask=FCGI_SOCKET_UMASK, multiplexed=True)
        srvr.run()
    finally:
        # clean up server socket file
        os.unlink(socketfile)

if __name__ == '__main__':
    main(sys.argv[1:])