"""Imports:
    sys: for console output
"""
import sys

def state(description):
    """Prints a description with no progress"""
    sys.stdout.write("%s...\n" % (description))

def skip(description):
    """Prints a description as having been skipped"""
    sys.stdout.write("%s... SKIPPED\n" % (description))

def report(description, total_units, done_units):
    """Prints a description with its total progress"""
    if done_units == total_units:
        sys.stdout.write("%s... 100%%\n" % (description))
        #sys.stdout.write("%s... %4d/%4d\n" % (description, done_units, total_units))
    else:
        percentage = (done_units / float(total_units)) * 100
        sys.stdout.write("%s... %3.0f%%\r" % (description, percentage))
        #sys.stdout.write("%s... %4d/%4d\r" % (description, done_units, total_units))
        sys.stdout.flush()
