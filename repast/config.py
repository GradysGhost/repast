#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.config
import os
import yaml

def deep_merge(base, to_merge):
    """Merges the contents of to_merge into base"""

    for key, value in list(to_merge.items()):
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            deep_merge(base[key], value)
        else:
            base[key] = value


class Config(dict):
    """Dictionary of options built from a config file"""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        if 'REPAST_CONFIG_FILE' in os.environ:
            self.parse_file(os.environ['REPAST_CONFIG_FILE'])
        else:
            self.parse_file()

    def parse_file(self, filename=None):
        if filename is None:
            filename = os.getcwd() + "/config.yml"

        try:
            data = yaml.load(open(filename, 'r'))
            deep_merge(self,data)
        except IOError:
            print("Could not open file for reading: %s" % filename)
        except ParserError:
            print("Could not parse config file: %s" % filename)

    def configure_logging(self):
        """Configures application logging"""

        default_format = '[%(asctime)s] [%(levelname)s] %(message)s'
        default_level = 'WARN'

        if 'logging' in self:
            log_format = self['logging']['format'] \
                if 'format' in self['logging'] else default_format

            log_level = self['logging']['level'] \
                if 'level' in self['logging'] else default_level
        else:
            log_format, log_level = default_format, default_level

        log_config = {
            'version' : 1,
            'formatters' : {
                'simple' : {
                    'format' : log_format
                }
            },
            'handlers' : {
                'console' : {
                    'class' : 'logging.StreamHandler',
                    'level' : log_level,
                    'formatter' : 'simple',
                    'stream' : 'ext://sys.stdout'
                }
            },
            'loggers' : {
                'stdout' : {
                    'level' : log_level,
                    'handlers' : [
                        'console'
                    ],
                    'propagate' : False
                }
            },
            'root' : {
                'level' : log_level,
                'handlers' : [
                    'console'
                ]
            }
        }
    
        try:
            logging.config.dictConfig(log_config)
        except Exception:
            print("Could not configure logging")

CONFIG = Config()
