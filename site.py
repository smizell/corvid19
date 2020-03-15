import os
import frontmatter
import markdown
import jinja2


class Site:
    def __init__(self, renderer, collection):
        self.renderer = renderer
        self.collection = collection

    def render_collection(self):
        for doc in self.collection.docs:
            if doc.file_name.endswith('.md'):
                doc.info.content = markdown.markdown(doc.info.content)
            doc.info.content = self.renderer.render(doc)


class Renderer:
    def __init__(self):
        loader = jinja2.FileSystemLoader(searchpath="./layouts")
        self.template_env = jinja2.Environment(loader=loader)
        self.template = self.template_env.get_template('main.jinja2')

    def render(self, doc):
        return self.template.render(doc=doc)


class Document:
    def __init__(self, file_name, info):
        self.file_name = file_name
        self.info = info

    @classmethod
    def from_file_name(cls, file_name):
        return cls(file_name, frontmatter.load(file_name))

    def __repr__(self):
        return f'Document({self.file_name})'


class Collection:
    def __init__(self, dir_name, docs):
        self.dir_name = dir_name
        self.docs = docs

    @classmethod
    def from_dir_name(cls, dir_name):
        docs = []
        for root, dirs, files in os.walk(dir_name):
            for f in files:
                docs.append(Document.from_file_name(os.path.join(root, f)))
        return cls(dir_name, docs)



collection = Collection.from_dir_name('./content')
site = Site(renderer=Renderer(), collection=collection)
site.render_collection()
print(site.collection.docs[0].info.content)
