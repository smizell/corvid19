import frontmatter
import jinja2

index = frontmatter.load('content/index.md')

templateLoader = jinja2.FileSystemLoader(searchpath="./layouts")
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template('main.jinja2')

print(template.render(content=index.content))
