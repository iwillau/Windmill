
import datetime

class Page:
    def __init__(self, name, path, content, **kwargs):
        self.name = name
        self.path = path
        self.content = content
        self.published = kwargs.pop('published', None)
        if self.published is not None:
            day, month, year = [int(i) for i in self.published.split('/')]
            self.published = datetime.date(year, month, day)

        self.metadata = kwargs

    @property
    def url(self):
        return '%s/%s.html' % (self.path, self.name)

class Blog(Page):
    pass
