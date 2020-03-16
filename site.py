import csv
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
DATA_DIR = './data'


class Renderer:
    def __init__(self, context):
        self.context = context
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
            return self.templates['page'].render(context=self.context, doc=doc)

        # Jinja2 files will render as themselves
        # There is no need to use a page template as the `extends` tag
        # can be used to load other templates
        if doc.file_name.endswith('.jinja2'):
            template = self.template_env.from_string(doc.info.content)
            doc.file_name = doc.file_name.replace('.jinja2', '.html')
            return template.render(context=self.context, doc=doc)

        # Everything else, we just send back the content
        return doc.info.content


class Context:
    def __init__(self):
        self.data = {}
        self.populate_data()

    def populate_data(self):
        for file_name in os.listdir(DATA_DIR):
            data_name, ext = file_name.split('.')
            if ext == 'csv':
                with open(os.path.join(DATA_DIR, file_name)) as f:
                    self.data[data_name] = list(csv.DictReader(f))


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


def load_docs():
    docs = []
    for dir_name, _, file_names in os.walk(CONTENT_DIR):
        for file_name in file_names:
            docs.append(Document.from_file_name(dir_name, file_name))
    return docs


def render(context, docs):
    renderer = Renderer(context)
    for doc in docs:
        doc.info.content = renderer.render(doc)


def prepare(docs):
    for doc in docs:
        doc.dir_name = doc.dir_name.replace('./content', './build')
        if doc.file_name.endswith('.html') and doc.file_name != 'index.html':
            final_dir_name = '.'.join(doc.file_name.split('.')[:-1])
            doc.dir_name = os.path.join(doc.dir_name, final_dir_name)
            doc.file_name = 'index.html'


def persist(docs):
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.mkdir(BUILD_DIR)

    # This support static files in the STATIC_DIR
    shutil.copytree(STATIC_DIR, os.path.join(BUILD_DIR, STATIC_DIR))

    # Persist each doc into the build directory
    # It will use whatever file name is there, so docs need to be prepared
    # and rendered by this point.
    for doc in docs:
        if os.path.exists(doc.dir_name) == False:
            pathlib.Path(doc.dir_name).mkdir(parents=True, exist_ok=True)
        full_path = os.path.join(doc.dir_name, doc.file_name)
        with open(full_path, 'w+') as f:
            f.write(doc.info.content)


def build():
    docs = load_docs()
    context = Context()
    render(context, docs)
    prepare(docs)
    persist(docs)


if __name__ == '__main__':
    print(f'Building site from {BUILD_DIR}')
    build()
