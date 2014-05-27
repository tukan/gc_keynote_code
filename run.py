import os
import subprocess
import numpy as np

RUNS = 10

def run(ruby_version, env=None):
	run_env = os.environ.copy()
	if env is not None:
		run_env.update(env)

	command = 'rbenv local %s && ruby -v rails_emulation_test.rb' % (ruby_version)
	print "%s %s" % (env, command)
	version = ''
	durations = []
	rss_s = []

	for _ in xrange(RUNS):
		output = subprocess.check_output(command, shell=True, env=env)
		output = output.split('\n')
		version = output[0]
		durations.append(float(output[1].split(' ')[1])) 
		rss_s.append(float(output[2].split(' ')[1]))
	
	print version
	print
	print "Duration min: %f" % np.min(durations)
	print "Duration max: %f" % np.max(durations)
	print "Duration median: %f" % np.median(durations)
	print
	print "RSS min: %f" % np.min(rss_s)
	print "RSS max: %f" % np.max(rss_s)
	print "RSS median: %f" % np.median(rss_s)
	print
	print "====================================================="
	print


if __name__ == "__main__":
	run('2.0.0-p353')
	run('2.1.2')
	run('2.2.0-dev')

	run('2.1.2', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '1.3'})
	run('2.1.2', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '0.9'})
	run('2.1.2', {'RUBY_GC_MALLOC_LIMIT_MAX': '8000000', 'RUBY_GC_OLDMALLOC_LIMIT_MAX': '8000000'})

	run('2.2.0-dev', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '1.3'})
	run('2.2.0-dev', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '0.9'})
	run('2.2.0-dev', {'RUBY_GC_MALLOC_LIMIT_MAX': '8000000', 'RUBY_GC_OLDMALLOC_LIMIT_MAX': '8000000'})
