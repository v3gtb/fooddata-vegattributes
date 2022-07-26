#!/usr/bin/env ruby
require 'jekyll'

s = Jekyll::Site.new(Jekyll.configuration({ "safe": true }))
s.read()
# TODO: this should be possible by taking the Document directly from the Site
# TODO: but I've had no success so far (.documents is empty, .pages has
# TODO: index.md as a Page but no idea what the relation to Documents is)
c = Jekyll::Collection.new(s, "some-label")
d = Jekyll::Document.new("index.md", { :site => s, :collection => c })
d.read()
r = Jekyll::Renderer.new(s, d)
info = {
  :registers        => { :site => s, :page => r.payload["page"] },
  :strict_filters   => true,
  :strict_variables => true,
}
output = r.render_liquid(d.content, r.payload, info, d.path)
File.write("_index-liquid-rendered.md", output)
