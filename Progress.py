import sys

def state(description):
    sys.stdout.write("%s...\n" % (description))

def report(description, total_units, done_units):
    if done_units == total_units:
        sys.stdout.write("%s... 100%%\n" % (description))
    else:
        percentage = (done_units / float(total_units)) * 100
        sys.stdout.write("%s... %3.0f%%\r" % (description, percentage))
        sys.stdout.flush()

