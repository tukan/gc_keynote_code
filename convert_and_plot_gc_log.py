#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import csv

READLINE_LIMIT = 1000


def convert_to_csv(source, dest):
  f = open(source, 'r')
  out = open(dest, 'w')
  line = f.readline(READLINE_LIMIT)
  while line is not None and len(line) > 0:
    out.write(line.replace('\t', ';'))
    line = f.readline(READLINE_LIMIT)

  f.close()
  out.close()


def load_csv(fname):
  res = []
  f = open(fname, 'r')
  reader = csv.DictReader(f, delimiter=';')
  for row in reader:
    res.append(row)
  f.close()
  return res


def plot_pair(first, second, title=None):
  import matplotlib.pyplot as plt

  fig, ((first_objs_ax, second_objs_ax), (first_time_ax, second_time_ax)) = plt.subplots(2, 2, sharex='col', sharey='row')

  if title is not None:
    fig.suptitle(title, size='large', weight='bold')

  _plot_objects(first_objs_ax, first['data'], title=first['title'], threegen=first['threegen'])
  _plot_objects(second_objs_ax, second['data'], title=second['title'], threegen=second['threegen'])

  _plot_time(first_time_ax, first['data'])
  _plot_time(second_time_ax, second['data'])

  plt.show()


def plot(boot, requests, title=None, threegen=True):
  import matplotlib.pyplot as plt

  fig, ((boot_obj_ax, requests_obj_ax), (boot_time_ax, requests_time_ax)) = plt.subplots(2, 2, sharex='col', sharey='row')

  if title is not None:
    fig.suptitle(title, size='large', weight='bold')

  _plot_objects(boot_obj_ax, boot, title=boot_title(boot), threegen=threegen)
  _plot_objects(requests_obj_ax, requests, title=requests_title(requests), threegen=threegen)

  _plot_time(boot_time_ax, boot)
  _plot_time(requests_time_ax, requests)

  plt.show()


def _plot_objects(ax, data, title=None, threegen=True):
  new_objs_count = []
  if threegen:
    young_objs_count = []
  old_objs_count = []
    
  for row in data:
    if threegen:
      new_objs_count.append(int(row['heap_live_slot']) - int(row['remembered_shady_object']) - int(row['old_object']) - int(row['young_object']))
      young_objs_count.append(int(row['young_object']))
    else:
      new_objs_count.append(int(row['heap_live_slot']) - int(row['remembered_shady_object']) - int(row['old_object']))

    old_objs_count.append(int(row['old_object']))
      
  ax.plot(new_objs_count, 'b-', label='new_object', zorder=0)
  if threegen:
    ax.plot(young_objs_count, 'r-', label='young_object', zorder=1)
  ax.plot(old_objs_count, 'g-', label='old_object', zorder=2)
  
  if title is not None:
    ax.set_title(title)
  
  ax.legend(loc='best')

def _plot_time(ax, data, title=None):
  ru_utimes = [0]
  ru_stimes = [0]
  ru_utime_last = int(data[0]['ru_utime'])
  ru_stime_last = int(data[0]['ru_stime'])

  for row in data[1:]:
    if row['type'] == 'gc_start':
      ru_utimes.append(ru_utimes[-1])
      ru_stimes.append(ru_stimes[-1])
    else:
      ru_utimes.append(int(row['ru_utime']) - ru_utime_last)
      ru_stimes.append(int(row['ru_stime']) - ru_stime_last)

    ru_utime_last, ru_stime_last = int(row['ru_utime']), int(row['ru_stime'])

  ax.plot(ru_utimes, 'm-', label='ru_utime diff')
  ax.plot(ru_stimes, 'c-', label='ru_stime diff')

  if title is not None:
    ax.set_title(title)

  ax.legend(loc='best')  


def requests_title(requests):
  minor_gc_count = int(requests[-1]['minor_gc_count']) - int(requests[0]['minor_gc_count'])
  major_gc_count = int(requests[-1]['major_gc_count']) - int(requests[0]['major_gc_count'])

  return "Requests: 100\n"\
          "Minor GC (%d): %f per request\n"\
          "Major GC (%d): %f per request" % (minor_gc_count, minor_gc_count/100, major_gc_count, major_gc_count/100)

def boot_title(boot):
  minor_gc_count = int(boot[-1]['minor_gc_count']) - int(boot[0]['minor_gc_count'])
  major_gc_count = int(boot[-1]['major_gc_count']) - int(boot[0]['major_gc_count'])

  return "Boot\n"\
          "Minor GC: %d\n"\
          "Major GC: %d" % (minor_gc_count, major_gc_count)  


if __name__ == "__main__":
  # convert_to_csv('boot-2.1.2.txt', 'boot-2.1.2.csv')
  convert_to_csv('requests-2.1.2.txt', 'requests-2.1.2.csv')
  convert_to_csv('requests.txt', 'requests.csv')  

  ruby_2_1_2_requests = load_csv('requests-2.1.2.csv')
  ruby_2_1_2 = {
    'data': ruby_2_1_2_requests,
    'title': "Ruby 2.1.2p95\n" + requests_title(ruby_2_1_2_requests),
    'threegen': False
  }

  ruby_2_2_requests = load_csv('requests.csv')
  ruby_2_2 = {
    'data': ruby_2_2_requests,
    'title': "Ruby 2.2.0-dev\n" + requests_title(ruby_2_2_requests),
    'threegen': True
  }

  plot_pair(ruby_2_1_2, ruby_2_2)

  # boot_data = load_csv('boot-2.1.2.csv')
  # requests_data = load_csv('requests-2.1.2.csv')

  # plot(boot_data, requests_data, title='ruby 2.1.2p95', threegen=False)
