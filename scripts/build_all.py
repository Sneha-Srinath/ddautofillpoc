"""Rebuild every demo asset:  python -m scripts.build_all

1. mock SQL database + extracted JSON   2. five fillable PDF templates
3. register the templates (company name + identifier)   4. Mock Data Report PDF
"""
from scripts import (build_data, build_data_report, build_docx_templates, build_html_templates,
                     build_templates, seed_templates)

if __name__ == "__main__":
    print("1/4 data:", build_data.build_db().name, "+", len(build_data.build_json()), "JSON files")
    print("2/4 templates:", len(build_templates.build_all()), "PDFs,", len(build_docx_templates.build_all()),
          "Word,", len(build_html_templates.build_all()), "web forms")
    print("3/4 registry:")
    seed_templates.run()
    print("4/4 report:", build_data_report.build().name)
