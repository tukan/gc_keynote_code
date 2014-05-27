obj = Object.new
100_000.times do |i|
  obj.respond_to?("sym#{i}".to_sym)
end
GC.start
puts"symbol : #{Symbol.all_symbols.size}"