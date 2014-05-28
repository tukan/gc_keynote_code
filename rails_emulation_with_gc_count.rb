require 'gc_tracer'
# require 'gctools/oobgc'
# require 'gctools/logger'

@retained = []
@rand = Random.new(999)

MAX_STRING_SIZE = 200
STATS_TO_COLLECT = [
  :heap_live_slot, 
  :old_object,
  :remembered_shady_object,
  :minor_gc_count,
  :major_gc_count
].freeze

def stress(allocate_count, retain_count, chunk_size, collect_gc_stats=false)
  chunk = []
  while retain_count > 0 || allocate_count > 0
    if retain_count == 0 || (@rand.rand < 0.5 && allocate_count > 0)
      chunk << " " * (@rand.rand * MAX_STRING_SIZE).to_i
      allocate_count -= 1
      if chunk.length > chunk_size
        chunk = []
        # GC::OOB.run if retain_count == 0
      end
    else
      @retained << " " * (@rand.rand * MAX_STRING_SIZE).to_i
      retain_count -= 1
    end
  end
end

def gc_stats_collector(stats_collection=nil)
  s = GC.stat
  res = {}
  STATS_TO_COLLECT.each do |k|
    res[k] = s[k]
  end 
  stats_collection << res if stats_collection
  res
end

def print_stats(stats)
  STATS_TO_COLLECT.each do |k|
    puts "#{k}: #{stats[k]}"
  end
  puts
end

start = Time.now

# simulate rails boot, 2M objects allocated 600K retained in memory
GC::Tracer.start_logging('boot-2.1.2.txt')
stress(2_000_000, 600_000, 200_000, false)
GC::Tracer.stop_logging
# boot_stats = gc_stats_collector()
# print_stats(boot_stats)

# simulate 100 requests that allocate 200K objects each
GC::Tracer.start_logging('requests-2.1.2.txt')
stress(20_000_000, 0, 200_000)
GC::Tracer.stop_logging
# boot_stats = gc_stats_collector()
# print_stats(boot_stats)

puts "Duration: #{(Time.now - start).to_f}"

puts "RSS: #{`ps -eo rss,pid | grep #{Process.pid} | grep -v grep | awk '{ print $1;  }'`}"