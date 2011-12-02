#!/usr/bin/env ruby
require "rubygems"
require "rack"
require "erb"

# install: Copy finder.cgi, finder.erb to #{Munin Document Root}/cgi/
# usage:   graph[]=pg_ => pg_* graph will display

class MuninFinder
  def call(env)
    params = Rack::Utils::parse_nested_query(env['QUERY_STRING'])
    list = images(params)
    menu = group_by(list)
    html = ERB.new(IO.read("finder.erb")).result(binding)
    [200, {"Content-Type" => "text/html"}, html.to_s]
  end

  def group_by(list)
    list.inject({:host=>[], :graph=>[]}) do |hash, png|
      host = File.dirname(png)
      hash[:host] << host unless hash[:host].include?(host)

      graph = File.basename(png, ".png").split("-")[0]
      hash[:graph] << graph unless hash[:graph].include?(graph)
      
      hash
    end
  end

  def images(params)
    yesterday = Time.now - (60*60*24)
    
    graph = %w(^cpu- ^load ^memory- ^process)
    if params['graph']
      graph += params['graph']
    end
    graph.map!{|x|Regexp.new(x)}

    at = %w(-day -week)
    at.map!{|x|Regexp.new(x)}
    
    Dir["../**/*.png"].select do |png|
      File.mtime(png) > yesterday && 
      graph.any?{|x|File.basename(png) =~ x} &&
      at.any?{|x|File.basename(png) =~ x}
    end.sort
  end
end

Rack::Handler::CGI.run(MuninFinder.new)
