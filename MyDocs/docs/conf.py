import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# Theme configuration
html_theme = 'sphinx_rtd_theme'

# Debugging information
print(f"Building with Python version: {sys.version}")
html_static_path = ['_static']
html_css_files = ['css/custom.css']
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
    "body_max_width": 'auto',  # Use full width
}
html_context = {
    'display_github': True,
    'github_user': 'Akt-AI',
    'github_repo': 'MyDocs',
    'github_version': 'main/docs/',
}

