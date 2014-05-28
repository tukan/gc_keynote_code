import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt

ENV = os.environ.copy()
RUNS = 10

def run(ruby_version, env=None):
  run_env = ENV.copy()
  if env is not None:
    run_env.update(env)
  
  command = 'rbenv local %s && ruby -v rails_emulation_test.rb' % (ruby_version)
  print "%s %s" % (env, command)
  version = ''
  durations = []
  rss_s = []

  for _ in xrange(RUNS):
    output = subprocess.check_output(command, shell=True, env=run_env)
    output = output.split('\n')
    version = output[0]
    durations.append(float(output[1].split(' ')[1])) 
    rss_s.append(float(output[2].split(' ')[1]))

  print version
  print
  print "Duration min: %f" % np.min(durations)
  print "Duration max: %f" % np.max(durations)
  print "Duration std: %f" % np.std(durations)
  print "Duration median: %f" % np.median(durations)
  print "Duration mean: %f" % np.mean(durations)
  print
  print "RSS min: %f" % np.min(rss_s)
  print "RSS max: %f" % np.max(rss_s)
  print "RSS std: %f" % np.std(rss_s)
  print "RSS median: %f" % np.median(rss_s)
  print "RSS mean: %f" % np.mean(rss_s)
  print
  print "====================================================="
  print

  return {
    'duration_mean': np.mean(durations),
    'duration_median': np.median(durations),
    'duration_std': np.std(durations),

    'rss_mean': np.mean(rss_s),
    'rss_median': np.median(rss_s),
    'rss_std': np.std(rss_s)
  }


def plot(labels, data, footnote=None):
  ## Data
  durations = [d['duration_mean'] for d in data]
  durations_std = [d['duration_std'] for d in data]

  rss_s = [d['rss_mean'] for d in data]
  rss_std = [d['rss_std'] for d in data]

  ind = np.arange(len(labels)) # the x locations for the groups array([0, 1, 2,...])
  width = 0.35        

  fig = plt.figure()

  ax = fig.add_subplot(111) # 1x1 grid, first subplot 

  ## the bars
  rec_durations = ax.bar(
    ind, durations, width,
    color='green',
    yerr=durations_std,
    error_kw=dict(elinewidth=2,ecolor='#3caa3c')
  )

  ax2 = ax.twinx()
  rec_rss = ax2.bar(
    ind+width, rss_s, width,
    color='blue',
    yerr=rss_std,
    error_kw=dict(elinewidth=2,ecolor='#007fff')
  )

  ## axes and labels
  ax.set_xlim(-width,len(ind)+width) # sets data limits for x-axis
  ax.set_ylabel('Duration')
  ax.set_xticks(ind+width) # Set the x ticks with list of ticks, accepts floats
  xtickNames = ax.set_xticklabels(labels)
  plt.setp(xtickNames, rotation=0, fontsize=10)

  ax2.set_xlim(-width,len(ind)+width)
  ax2.set_ylabel('RSS')

  ## add a legend
  fig.legend((rec_durations[0], rec_rss[0]), ('Duration', 'RSS'), 
            loc='upper center', 
            fancybox=True,
            shadow=True)
      
  if footnote is not None:
    fig.subplots_adjust(bottom=0.15)            
    fig.text(0.28, 0.03, footnote, ha='left', bbox=dict(boxstyle="square,pad=0.3", fc="w"))
  
  plt.show()


if __name__ == "__main__":
  labels = []
  data = []

  # for version in ('1.9.3-p545', '2.0.0-p353', '2.1.2', '2.2.0-dev'):
  for version in ('2.1.2', '2.2.0-dev'):
    data.append(run(version))
    labels.append(version)
	
  labels.append('2.1.2 [1]')
  data.append(run('2.1.2', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '1.3'}))

  labels.append('2.1.2 [2]')
  data.append(run('2.1.2', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '0.9'}))

  labels.append('2.1.2 [3]')
  data.append(run('2.1.2', {'RUBY_GC_HEAP_INIT_SLOTS': '600000', 'RUBY_GC_HEAP_FREE_SLOTS': '1600000'}))

  labels.append('2.1.2 [4]')
  data.append(run('2.1.2', {'RUBY_GC_MALLOC_LIMIT_MAX': '8000000', 'RUBY_GC_OLDMALLOC_LIMIT_MAX': '8000000'}))

  labels.append('2.2.0-dev [1]')
  data.append(run('2.2.0-dev', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '1.3'}))

  labels.append('2.2.0-dev [2]')
  data.append(run('2.2.0-dev', {'RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR': '0.9'}))

  labels.append('2.2.0-dev [3]')
  data.append(run('2.2.0-dev', {'RUBY_GC_HEAP_HEAP_SLOTS': '600000', 'RUBY_GC_HEAP_FREE_SLOTS': '1600000'}))

  labels.append('2.2.0-dev [4]')
  data.append(run('2.2.0-dev', {'RUBY_GC_MALLOC_LIMIT_MAX': '8000000', 'RUBY_GC_OLDMALLOC_LIMIT_MAX': '8000000'}))

  footnote = '[1] RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR=1.3\n'\
              '[2] RUBY_GC_HEAP_OLDOBJECT_LIMIT_FACTOR=0.9\n'\
              '[3] RUBY_GC_HEAP_INIT_SLOTS=600000 RUBY_GC_HEAP_FREE_SLOTS=1600000\n'\
              '[4] RUBY_GC_MALLOC_LIMIT_MAX=8000000 RUBY_GC_OLDMALLOC_LIMIT_MAX=8000000'

  plot(labels, data, footnote=footnote)
