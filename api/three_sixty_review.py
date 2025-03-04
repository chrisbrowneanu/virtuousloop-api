import jinja2
from flask import Blueprint, Response, request
from weasyprint import HTML
import unidecode
import api.functions as fn

# import pandas as pd
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
import numpy as np
from io import StringIO
from statistics import mean
import random

three_sixty_review = Blueprint("three_sixty_review", __name__)

@three_sixty_review.route("/three_sixty_review", methods = ['POST'])
def feedback_three_sixty_review():
    """turns the marks json into css feedback"""

    # load the jinja environment
    loader = jinja2.FileSystemLoader(searchpath=fn.template_path())
    env = jinja2.Environment(loader=loader)

    # take the POST json, and merge it with the default variables needed in the template

    variables = request.get_json()
    chart = build_stripplot(variables)

    # load the template
    template = env.get_template(variables['summary']['pdf_template'] + ".html")
    stylesheet = fn.stylesheet_path(variables['summary']['pdf_stylesheet'])


    # build the pdf
    try:
        html_out = template.render(variables=variables,
                               chart=chart)
        converted = html_out.encode('ascii',errors='ignore').decode('ascii')
        print("pdf complete")
        pdf_out = HTML(string=converted).write_pdf(stylesheets=[stylesheet])
    except Exception:
        converted = ""
        pdf_out = HTML(string=converted).write_pdf(stylesheets=[stylesheet])
        app.logger.debug("Exception on pdf_out")

    # return the pdf
    return Response(pdf_out, mimetype="application/pdf")

def build_crit_labels(var):
    row = []
    for crit in var:
        if 'crit' in crit['field']:
            row.append(crit['description'])
    return row

def build_xticklabels(levels):
    row = []
    for level in levels:
        if level['display'] == "show":
            row.append(level['label'])
    return row

def build_xticks(levels):
    row = []
    for level in levels:
        if level['display'] == "show":
            row.append(int(level['level']))
    return row

def build_colorpalette(roles):
    palette = {}
    for role in roles:
        palette[role['role']] = role['palette']
    return palette

def get_level(variables, v):
    if v != '':
        for level in variables['levels']:
            if v.lower() == level['label'].lower():
                rand = random.uniform(-0.15, 0.15)
                res = float(level['level']) + rand
    else:
        res = ""
    return res

def build_data(variables):
    crit_list, role_list, value_list = [], [], []
    for crit in variables['fields']:
        if 'crit' in crit['field']:
            for record in variables['records']:
                for k, v in record.items():
                    if k.lower() == crit['field']:
                        crit_list.append(k)
                        value_list.append(get_level(variables, v))
                    if k.lower() == 'role':
                        role_list.append(v)

    crit_fields = list(set(crit_list))
    for crit_field in crit_fields:
        crit_field_vals = []
        for i, crit in enumerate(crit_list):
            if crit_field == crit:
                if value_list[i]:
                    this_val = float(value_list[i])
                    crit_field_vals.append(this_val)
        this_ave = float(mean(crit_field_vals))
        crit_list.append(crit_field)
        value_list.append(this_ave)
        role_list.append("Average")


    df = pd.DataFrame(
        {
            'crit_list': crit_list,
            'value_list': value_list,
            'role_list': role_list,
        }
    )

    df['value_list'].replace('', np.nan, inplace=True)
    df.dropna(subset=['value_list'], inplace=True)
    df.sort_values(by=['crit_list','value_list'], inplace=True)
    return df

def build_stripplot(variables):
#     '''stripplot with each crit and eye'''

    this_df = build_data(variables)
    palette_map = build_colorpalette(variables['roles'])
    crit_labels = build_crit_labels(variables['fields'])
    xticks = build_xticks(variables['levels'])
    xticklabels = build_xticklabels(variables['levels'])

    sns.set(rc={'figure.figsize': (8, 3)})
    sns.set_style("ticks")

    ax = sns.stripplot(x='value_list', y='crit_list', hue='role_list',
                       data=this_df, s=10, alpha=0.6, jitter=True,
                       palette=palette_map, native_scale=False)


    ax.set_xlabel("")
    ax.set_ylabel("")

    ax.set_xticks(xticks)
    ax.set_xlim([-2.5, 2.5])

    ax.set_xticklabels(xticklabels, rotation=0, va="center")
    ax.set_yticklabels(crit_labels)

    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_linewidth(0.2)

    ax.grid(color='gray', axis='y', linestyle='solid', linewidth=0.5)
    ax.tick_params(direction='inout', length=10, width=0.5, color='gray', pad=10)

    chartBox = ax.get_position()
    ax.set_position([0.3, 0.3, chartBox.width * 0.7, chartBox.height * 0.9])
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.5), ncol=3)

    i = StringIO()
    plt.savefig(i, format="svg")
    fig = i.getvalue()
    plt.clf()

    return fig