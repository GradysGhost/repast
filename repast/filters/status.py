#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask
import logging as log
import repast


class Filter(repast.BaseFilter):
    def __init__(self):
        defaults = { 'message': 'OK',
                     'content-type': 'text/plain',
                     'route': '/status/repast' }

        if 'status' not in repast.app.CONFIG:
            repast.app.CONFIG['status'] = defaults

        statconf = repast.app.CONFIG['status']
        if 'message' not in statconf:
            statconf['message'] = defaults['message']
            statconf['content-type'] = defaults['content-type']
        if 'content-type' not in statconf:
            statconf['content-type'] = defaults['content-type']

    def apply(self, request):
        return request

@repast.app.route('/repast/status', methods=[ 'GET' ])
def handle_get_status():
    response = flask.make_response(repast.app.CONFIG['status']['message'])
    response.headers['Content-Type'] = repast.app.CONFIG['status']['content-type']
    return response

