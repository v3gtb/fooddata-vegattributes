#!/usr/bin/env ruby
require 'jekyll'

Jekyll::PluginManager.require_from_bundler
s = Jekyll::Site.new(Jekyll.configuration({}))
s.reset()
s.read()
s.generate()
p = s.pages.detect { |p| p.path == "index.md" }
r = Jekyll::Renderer.new(s, p)
info = {
  :registers        => { :site => s, :page => r.payload["page"] },
  :strict_filters   => true,
  :strict_variables => true,
}
output = r.render_liquid(p.content, r.payload, info, p.path)
File.write("_index-liquid-rendered.md", output)
