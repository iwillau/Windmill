
import logging, os
from datetime import datetime
from windmill.page import Page, Blog
from windmill.parsers import Markdown
from mako.lookup import TemplateLookup

log = logging.getLogger(__name__)

class Generator:
    def __init__(self, base):
        self.base = base
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

        self.templates = TemplateLookup(directories=[os.path.join(base, 'source')], 
                                        input_encoding='utf-8',
                                        output_encoding='utf-8',
                                        module_directory=self.data
                                       )

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

        log.debug('Checking source for updated files')
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
            generating_time = datetime.now()
            log.info('Source is newer. Generating Site as of %s.' %
                     generating_time)
            # Pass 1. Create Page Objects. Weed out non Pages
            self.pages = []
            for filename, filepath in pages:
                 pagename, pageext = os.path.splitext(filename)
                 if pageext in self.parsers:
                     fp = open(os.path.join(self.source, filepath, filename))
                     try:
                         pagetype, metadata, content = self.parsers[pageext].parse(fp)
                         page=(self.types[pagetype](pagename,
                                                     filepath,
                                                     content=content,
                                                     **metadata))
                         if page.published and page.published <= generating_time.date():
                             self.pages.append(page)
                     except Exception, e:
                         log.error('Could not parse file: %s (%s)' % (filename, e))
                    
            # Pass 2. Assign a Template to each Page
            for page in self.pages:
                try:
                    page.template = self.templates.get_template(page.template_name)
                except Exception, e:
                    log.error('Error on page %s. (%s)' % (page.name, e))
            # Pass 3. Render each page onto the filesystem
            for page in self.pages:
                try:
                    rendered_file = os.path.join(self.static, page.path,
                                                 page.name+'.html')
                    rfp = open(rendered_file, 'w')
                    rfp.write(page.template.render(windmill=self, page=page))
                    rfp.close()
                except Exception, e:
                    log.error('Error rendering page %s. (%s)' % (page.name, e))

            fp = open(generated_file,'w')
            fp.write(generating_time.strftime('%d/%m/%Y %H:%M:%S'));
            fp.close()
        

