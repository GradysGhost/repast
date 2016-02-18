#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask
import logging as log
import repast


class Filter(repast.BaseFilter):
    def __init__(self):
        if 'headernorm' not in repast.app.CONFIG:
            raise repast.ConfigurationError(
                'headernorm plugin is unconfigured')

    def make_bad_request_response(self, message):
        log.info("Header normalization filter has found a problem: %s" % message)
        return flask.make_response(message, 400)
      
    def add(self, req):
        # Add some headers to the request
        to_add = repast.app.CONFIG['headernorm']['add']
        for header in to_add:
            req.headers.update({header: to_add[header]})
        return req

    def remove(self, req):
        # Remove some headers from the request
        to_remove = repast.app.CONFIG['headernorm']['remove']
        for header in to_remove:
            if header.lower() in [ r.lower() for r in req.headers ]:
                # Remove a header if it matches a specific value
                if isinstance(to_remove[header], str):
                    if req.headers[header] == to_remove[header]:
                        del req.headers[header]
                        
                # Remove a header if it matches one of a list of values
                elif isinstance(to_remove[header], list):
                    if req.headers[header] in to_remove[header]:
                        del req.headers[header]

                # Remove a header if it exists, regardless of its value
                elif to_remove[header] is None:
                    del req.headers[header]

                else:
                    raise TypeError()

        return req

    def require(self, req):
        # Require some headers, maybe with specific values
        required_headers = repast.app.CONFIG['headernorm']['require']
        for header in required_headers:
            print([ r.lower() for r in req.headers ])
            if header.lower() not in [ r.lower() for r in req.headers ]:
                return self.make_bad_request_response(
                    'Required header "%s" not found in request' % header)
            else:
                # Config requires a specific string match
                if isinstance(required_headers[header], str):
                    if req.headers[header] != required_headers[header]:
                        return self.make_bad_request_response(
                            'Header "%s" must be set to "%s"' %
                            ( req.headers[header], required_headers[header] ))

                # Config requires one of a list of valid options
                elif isinstance(required_headers[header], list):
                    if req.headers[header] not in required_headers[header]:
                        return self.make_bad_request_response(
                            'Header "%s" not set to a valid value' % header)

                # The header is not a str, list, or NoneType
                elif required_headers[header] is not None:
                    raise TypeError()
                
                return req

    def apply(self, req):
        if 'remove' in repast.app.CONFIG['headernorm']:
            req = self.remove(req)
        
        if 'add' in repast.app.CONFIG['headernorm']:
            req = self.add(req)

        if 'require' in repast.app.CONFIG['headernorm']:
            req = self.require(req)

        return req



