import os
import pathlib
import shutil
import frontmatter
import markdown
import jinja2


BUILD_DIR = './build'
CONTENT_DIR = './content'
LAYOUTS_DIR = './layouts'
STATIC_DIR = './static'


class Site:
    def __init__(self, renderer, docs):
        self.renderer = renderer
        self.docs = docs

    def render(self):
        for doc in self.docs:
            doc.info.content = self.renderer.render(doc)

    def persist(self, dir_name=BUILD_DIR):
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.mkdir(BUILD_DIR)
        shutil.copytree(STATIC_DIR, os.path.join(BUILD_DIR, STATIC_DIR))
        for doc in self.docs:
            path = doc.dir_name.replace('./content', './build')
            if os.path.exists(path) == False:
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            new_full_path = os.path.join(path, doc.file_name)
            with open(new_full_path, 'w+') as f:
                f.write(doc.info.content)


class Renderer:
    def __init__(self):
        loader = jinja2.FileSystemLoader(searchpath=LAYOUTS_DIR)
        self.template_env = jinja2.Environment(loader=loader)
        self.templates = {
            # 'main': self.template_env.get_template('main.jinja2'),
            'page': self.template_env.get_template('page.jinja2'),
        } 

    def render(self, doc):
        # Markdown uses the page template
        if doc.file_name.endswith('.md'):
            doc.info.content = markdown.markdown(doc.info.content)
            doc.file_name = doc.file_name.replace('.md', '.html')
            return self.templates['page'].render(doc=doc)

        # Jinja2 files will render as themselves
        # There is no need to use a page template as the `extends` tag
        # can be used to load other templates
        if doc.file_name.endswith('.jinja2'):
            template = self.template_env.from_string(doc.info.content)
            doc.file_name = doc.file_name.replace('.jinja2', '.html')
            return template.render(doc=doc)

        # Everything else, we just send back the content
        return doc.info.content


class Document:
    def __init__(self, dir_name, file_name, info):
        self.dir_name = dir_name
        self.file_name = file_name
        self.info = info

    @classmethod
    def from_file_name(cls, dir_name, file_name):
        return cls(dir_name, file_name, frontmatter.load(os.path.join(dir_name, file_name)))

    def __repr__(self):
        return f'Document({self.dir_name}/{self.file_name})'


def build_docs(dir_name):
    docs = []
    for root, dirs, files in os.walk(dir_name):
        for f in files:
            docs.append(Document.from_file_name(root, f))
    return docs


site = Site(renderer=Renderer(), docs=build_docs(CONTENT_DIR))
site.render()
site.persist()
