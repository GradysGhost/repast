#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask
import importlib
import logging as log

from repast.config import CONFIG
from requests import Request, Session


class BaseFilter:
    '''An "interface", so to speak, for Repast filters'''
    def __init__(self):
        raise NotImplementedError(
            "A filter's constructor should be used for config validation and other startup tasks.")

    def apply(self, request):
        raise NotImplementedError(
            "The 'apply' function should be used to apply the effects of a filter.")


class RepastRequest(object):
    '''Converts Flask request data into a manipulatable class'''
    def __init__(self, flaskreq):
        self.method = flaskreq.method
        self.body = flaskreq.data
        self.path = flaskreq.path
        self.headers = dict()

        for header in flaskreq.headers:
            self.headers[header[0].lower()] = header[1]

    def __repr__(self):
        return 'RepastRequest<method="%s", path="%s", headers=%s, body=%s>' % (
            self.method, self.path, self.headers, self.body)

class ConfigurationError(Exception):
    pass

def run():
    '''Runs the Repast app'''
    app.run(host=CONFIG['bind']['address'],
            port=CONFIG['bind']['port'])


CONFIG.configure_logging()
log.info('Repast startup...')
log.info('Logging configured')

app = flask.Flask(__name__)
app.CONFIG = CONFIG

# Load filters
CONFIG['filter_instances'] = dict()
for filt in CONFIG['filters']:
    log.info('Importing filter: %s' % filt)
    importlib.import_module('repast.filters.%s' % filt)
    CONFIG['filter_instances'][filt] = eval('filters.%s.Filter()' % filt)
    log.info('Import finished: %s' % filt)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handle_request(path):
    request = RepastRequest(flask.request)

    for filt in CONFIG['filter_instances']:
        request = CONFIG['filter_instances'][filt].apply(request)
        if isinstance(request, flask.wrappers.Response):
            return request

    s = Session()
    backend_request = Request(
        request.method,
        CONFIG['backend'] + request.path,
        data=request.body,
        headers=request.headers
    ).prepare()
    backend_response = s.send(backend_request)
    print(backend_response.headers)
    return flask.make_response((
        backend_response.content,
        backend_response.status_code,
        backend_response.headers.items()
    ))

