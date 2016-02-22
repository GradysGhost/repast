# Repast

A Python HTTP request manipulator


## Model

Repast is essentially an HTTP proxy service that manipulates inbound requests
before forwarding them to the backend. The manipulations are performed by a
series of _filters_.


## Configuration

You may specify a configuration file to load with the `REPAST_CONFIG_FILE`
environment variable. If you do not provide one, Repast will try to load from
`./config.yml`.

The configuration file should be YAML formatted.

### Required Options

 * `bind` - A dictionary describing the listening socket, containing:
   * `address` - The IP address to bind to
   * `port` - The port to bind to
 * `backend` - A string describing the server to proxy requests to.
 * `filters` - A list of filters to load, _in the order you want them to
    be applied_.

### Optional Options

 * `ssl` - When present, this dictionary configures SSL on the listener. Note
   that if you enable SSL and use an unencrypted backend, Repast can serve as an
   SSL terminator.
   * `cert` - The file path to the SSL certificate
   * `key` - The file path to the SSL key

### Configuring Filters

Filters may require additional configuration. See the individual filter docs for
their configuration details.


## Filters

### headernorm

The `headernorm` filter performs request header normalization by removing,
adding, or requiring certain headers or header values, _in that order_.

**All header name comparisons are case-insensitive. All header value comparisons
are case-sensitive.**

#### headernorm Configuration

Configure `headernorm` by adding a config stanza called `headernorm` to the main
Repast config file.

##### Header Removal

To remove headers, configure them in a dict called `remove`. Each header can be
set to one of three different values. When set to a list, the header will be
removed if the value of the header in the inbound request matches one of the
values in the list:

    headernorm:
      remove:
        accept:
          - text/xml
          - text/html

When set to a string, the header is removed if it matches that one string:

    headernorm:
      remove:
        accept: text/xml

When set to Null, the header is removed if it is present, regardless of value:

    headernorm:
      remove:
        accept: Null

##### Header Addition

To have the filter add headers, configure them in a dict called `add`, like so:

    headernorm:
      add:
        Accept: application/json
        User-Agent: curl

##### Header Requirement

To have the filter require certain headers, configure them in a dict called
`require`. In similar fashion to header removal, headers can be required to be
set to a specific value, one of a collection of possible values, or simply to be
present with any value.

To match one of a handful of values:

    headernorm:
      require:
        accept:
          - application/json
          - text/xml

To match a single value:

    headernorm:
      require:
        accept: application/json

To accept any value:

    headernorm:
      require:
        accept: Null

#### Practical Configuration

Consider this situation: you have a REST API that only communicates in JSON. You
can normalize any request to force 'Accept: application/json' with a config like
this one:

    headernorm:
      remove:
        accept: Null
      add:
        Accept: application/json
      require:
        accept: application/json

Recall that regardless of how they are sequenced in your config, `headernorm`
will always process header removal, addition, and requirement in that order.
So the above config has the effect of removing any Accept header that exists,
adding in the proper Accept header, and then verifying that the header is
properly set. In this way, even if a request is made asking for an XML
response, the request will be converted to asking for JSON before going to the
backend.

### status

Adds a route to check Repast's status. By default, a `text/plain` message
saying `OK` will be returned on `GET` calls to `/repast/status`. This default
behavior requires no additional configuration beyond including the filter in
the filter list. You can optionally override the message and `Content-Type`
header with some simple config:

    status:
      message: '{"message":"OK"}'
      content-type: 'application/json'


## Developing Filters

A filter is a class called Filter that inherits `repast.BaseFilter` and
overrides its constructor and its `apply` function. The constructor will get
called during the server's startup procedure, and should be used to validate
configs or do other startup tasks. The apply function should accept a
`RepastRequest` object and should return either the modified `RepastRequest` to
pass the request to the next filter or backend, or a Flask response to abort the
request and respond.

