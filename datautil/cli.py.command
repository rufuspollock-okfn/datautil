import sys
import os
import optparse
import logging
from StringIO import StringIO
import traceback
import time

parser = optparse.OptionParser()

parser.add_option(
    '-v', '--verbose',
    dest='verbose',
    action='count',
    default=0,
    help='Give more output')
parser.add_option(
    '-q', '--quiet',
    dest='quiet',
    action='count',
    default=0,
    help='Give less output')

class Command(object):
    name = None
    usage = None
    default_parser = None
    all_commands = []

    def __init__(self):
        assert self.name
        self.parser = optparse.OptionParser(
            usage=self.usage,
            prog='%s %s' % (sys.argv[0], self.name),
            version=parser.version)
        for option in self.default_parser.option_list:
            if not option.dest:
                # -h, --version, etc
                continue
            self.parser.add_option(option)
        Command.all_commands[self.name] = self

    def merge_options(self, initial_options, options):
        for attr in ['log']:
            setattr(options, attr, getattr(initial_options, attr) or getattr(options, attr))
        options.quiet += initial_options.quiet
        options.verbose += initial_options.verbose

    def main(self, complete_args, args, initial_options):
        options = initial_options
        discarded_options, args = self.parser.parse_args(args)
        # From pip but not needed by us I think
        # self.merge_options(initial_options, options)
        self.options = options
        self.verbose = options.verbose

        level = 1
        level += options.verbose
        level -= options.quiet
        complete_log = []
        if options.log:
            log_fp = open_logfile_append(options.log)
            logger.consumers.append((logger.DEBUG, log_fp))
        else:
            log_fp = None

        exit = 0
        try:
            self.run(options, args)
        except:
            logger.fatal('Exception:\n%s' % format_exc())
            exit = 2
        
        if log_fp is not None:
            log_fp.close()
        if exit:
            log_fn = 'datapkg-log.txt'
            text = '\n'.join(complete_log)
            # Not sure we need to tell people ...
            # logger.fatal('Storing complete log in %s' % log_fn)
            log_fp = open_logfile_append(log_fn)
            log_fp.write(text)
            log_fp.close()
        sys.exit(exit)
