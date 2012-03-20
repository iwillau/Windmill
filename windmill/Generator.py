#!/usr/bin/env python
###########################################################
#
# Generate Website
#
# This is the main script to generate the website.
# Looks for all of the mako/md files in source
# and generates the HTML for static consumption
#
###########################################################

import logging, ConfigParser, os, datetime
from logging.config import fileConfig
from markdown import Markdown
from mako.lookup import TemplateLookup

log = logging.getLogger()

class Page:
    pass

class Generator:
    def __init__(self, config):
        self.config = config
        self.markdown = Markdown(
                            output_format='html5',
                        )

        templates = os.path.join(self.config.get('generate:main','base'),'source')
        self.template = TemplateLookup(directories=[templates], 
                                       input_encoding='utf-8',
                                       output_encoding='utf-8')

    def update(self):
        '''
        Firstly we loop through the source, and look for an mtime greater than
        the last generation. If we find one, then we generate.
        '''
        generated = datetime.datetime(1900,1,1)
        source = os.path.join(self.config.get('generate:main','base'),'source')
        dest = os.path.join(self.config.get('generate:main','base'),'static')
        log.info('Checking source in %s' % source)
        pages = []
        newer = False
        for dir, dirs, files in os.walk(source):
            for f in files:
                if f[-3:] == '.md':
                    pages.append([f[:-3], dir[len(source)+1:]])
                    mtime = datetime.datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(dir,f)))
                    if not newer and mtime > generated:
                        newer = True
        if newer:
            processed_pages = []
            log.info('Change detected. Re-generating.')
            for f, dir in pages:
                file_path = os.path.join(source, dir, f) + '.md'
                meta, content = self._process_markdown(open(file_path))
                if meta['template'] is None:
                    meta['template'] = os.path.join(dir,f)
                meta['template'] = meta['template'] + '.mako'
                processed_pages.append({'meta':meta, 
                                        'content': content,
                                        'name': f,
                                        'dir': dir,
                                       })
            self.pages = processed_pages
            for page in self.pages:
                log.debug('Rendering %s' % page['name'])
                rendered = self._template(page['meta'], page['content'])
                rendered_dir = os.path.join(dest,page['dir'])
                if not os.path.isdir(rendered_dir):
                    os.mkdir(rendered_dir)
                rendered_file = os.path.join(dest,page['dir'],page['name']) + '.html'
                rfp = open(rendered_file, 'w')
                rfp.write(rendered)
                rfp.close()



    def _process_markdown(self, fp):
        meta = {
            'template': None,
            'published': None,
            'tags': None,
        }
        def read_file():
            in_head = True
            for line in fp:
                if not in_head:
                    yield line
                else:
                    if len(line) < 2:
                        in_head = False
                        yield line
                    else:
                        name, value = line.split(':')
                        meta[name.lower()] = value.strip()

        
        content = self.markdown.convert(''.join(read_file()))
        self.markdown.reset()
        if meta['published'] is not None:
            day, month, year = [int(i) for i in meta['published'].split('/')]
            meta['published'] = datetime.date(year, month, day)
        if meta['tags']:
            meta['tags'] = [t.strip() for t in meta['tags'].split(',')]
        else:
            meta['tags'] = []

        return meta, content

    def _template(self, meta, content):
        template = self.template.get_template(meta['template'])
        return template.render(content=content, windmill=self, **meta)

if __name__ == '__main__':
    config_file = 'generate.ini'
    config_file = os.path.abspath(config_file)
    parser = ConfigParser.SafeConfigParser()
    parser.read([config_file])
    fileConfig([config_file])
    if not parser.has_option('generate:main', 'base'):
        if not parser.has_section('generate:main'):
            parser.add_section('generate:main')
        parser.set('generate:main','base',os.path.dirname(config_file))

    g = Generator(parser)
    g.update()
