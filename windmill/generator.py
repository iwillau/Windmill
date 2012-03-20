
import logging, os
from datetime import datetime
from windmill.page import Page, Blog
from windmill.parsers import Markdown

log = logging.getLogger(__name__)

class Generator:
    def __init__(self, base):
        self.base = base
        self.templates = os.path.join(base,'source')
        self.source = os.path.join(base,'source')
        self.static = os.path.join(base,'static')
        self.data = os.path.join(base,'data')

        self.parsers = {
            '.md': Markdown(),
        }

        self.types = {
            'page': Page,
            'blog': Blog,
        }

#         self.template_fetcher = TemplateLookup(directories=[self.templates], 
#                                                input_encoding='utf-8',
#                                                output_encoding='utf-8',
#                                                module_directory=self.data
#                                               )
# 
    def update(self):
        '''
        Firstly we loop through the source, and look for an mtime greater than
        the last generation. If we find one, then we generate.

        If we are newer, and have to generate, we make a couple of passes
        1. Generate the Page Object for each file
        2. Let them parse their own contents
        3. Pass them to the templater
        '''
        generated_file = os.path.join(self.static, 'generated.txt')
        try:
            fp = open(generated_file,'r')
            gen_string = fp.readline()
            fp.close()
            generated = datetime.strptime(gen_string, '%d/%m/%Y %H:%M:%S')
        except Exception, e:
            generated = datetime(1900,1,1)
        generated = datetime(1900,1,1)

        log.info('Checking source for updated files')
        pages = []
        newer = False
        for dir, dirs, files in os.walk(self.source):
            for f in files:
                pages.append([f, dir[len(self.source)+1:]])
                mtime = datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(dir,f)))
                if not newer and mtime > generated:
                    newer = True

        if newer:
            log.info('Source is newer. Generating Site.')
            # Pass 1. Create Page Objects. Weed out non Pages
            self.pages = []
            for filename, filepath in pages:
                 pagename, pageext = os.path.splitext(filename)
                 if pageext in self.parsers:
                     fp = open(os.path.join(self.source, filepath, filename))
                     try:
                         pagetype, metadata, content = self.parsers[pageext].parse(fp)
                         self.pages.append(self.types[pagetype](pagename,
                                                                filepath,
                                                                content=content,
                                                                **metadata))
                     except Exception, e:
                         log.error('Could not parse file: %s (%s)' % (filename, e))
                    
            # Pass 2. Let Page Objects Parse their contents.
            #         Assign a Template to each Page
            for page in self.pages:
                pass
            # Pass 3. Render each page onto the filesystem
            for page in self.pages:
                pass
            # page.template.render(generator=self, page=page)

            fp = open(generated_file,'w')
            fp.write(datetime.now().strftime('%d/%m/%Y %H:%M:%S'));
            fp.close()
        

        return
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

    def get_template(self, meta, content):
        template = self.template.get_template(meta['template'])
        return template.render(content=content, windmill=self, **meta)

