import jinja2
from flask import Blueprint, Response, request
from weasyprint import HTML
import unidecode
import api.functions as fn

rubric = Blueprint("rubric", __name__)

@rubric.route("/rubric", methods = ['POST'])
def feedback_rubric():
    """turns the marks json into css feedback"""

    # load the jinja environment
    loader = jinja2.FileSystemLoader(searchpath=fn.template_path())
    env = jinja2.Environment(loader=loader)

    # take the POST json, and merge it with the default variables needed in the template
    variables = request.get_json()
    rubric = build_rubric(variables)

    # load the template
    template = env.get_template("feedback_rubric.html")
    stylesheet = fn.stylesheet_path(variables['summary']['pdf_stylesheet'])

    # build the pdf
    try:
        html_out = template.render(variables=variables,
                               rubric=rubric)
        converted = html_out.encode('ascii',errors='ignore').decode('ascii')

        pdf_out = HTML(string=converted).write_pdf(stylesheets=[stylesheet])
    except Exception:
        converted = ""
        pdf_out = HTML(string=converted).write_pdf(stylesheets=[stylesheet])
        app.logger.debug("Exception on pdf_out")

    # return the pdf
    return Response(pdf_out, mimetype="application/pdf")


def build_rubric(variables):
    res = []
    for crit in variables['fields']:
        if 'crit' in crit['field']:
            row = []
            for col in variables['levels']:
                for cell in variables['desc']:
                    if 'crit' in crit['field'] and col['display'] == 'show' and crit['field'] == cell['field'] and col['level'] == cell['level']:

                        # note uses records[0] - rubric only returns first result
                        for k,v in variables['records'][0].items():
                            if k.lower() == crit['field']:
                                for level_item_find in variables['levels']:
                                  if v == level_item_find['level']:
                                      if level_item_find['class1'] == col['level'] and level_item_find['class2'] == col['level']:
                                          background = 'b100'
                                      elif level_item_find['class1'] == col['level'] or level_item_find['class2'] == col['level']:
                                          background = 'b50'
                                      else:
                                          background = 'b0'
                        row.append({'level': cell['level'],
                                    'description': cell['description'],
                                    'background': background})
            crit['row'] = row
            res.append(crit)
    return res