import os
import jinja2
import pytest

def test_templates_syntax():
    """
    Load all templates and check for syntax errors.
    """
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'ui', 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_dir))
    
    # Add custom filters used in server.py
    def from_json(value): return []
    env.filters["from_json"] = from_json

    template_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
    
    for template_file in template_files:
        try:
            env.get_template(template_file)
        except jinja2.exceptions.TemplateSyntaxError as e:
            pytest.fail(f"Syntax error in template {template_file} at line {e.lineno}: {e.message}")
        except Exception as e:
            pytest.fail(f"Error loading template {template_file}: {str(e)}")
