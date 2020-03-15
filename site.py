import frontmatter
import jinja2


class Site:
    def __init__(self, renderer):
        self.renderer = renderer


class Renderer:
    def __init__(self):
        loader = jinja2.FileSystemLoader(searchpath="./layouts")
        self.template_env = jinja2.Environment(loader=loader)
        self.template = self.template_env.get_template('main.jinja2')

    def render(self, doc):
        return self.template.render(doc=doc)


class Document:
    def __init__(self, filename, info):
        self.info = info

    @classmethod
    def from_filename(cls, filename):
        return cls(filename, frontmatter.load(filename))


site = Site(renderer=Renderer())
doc = Document.from_filename('content/index.md')

print(site.renderer.render(doc))
