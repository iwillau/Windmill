from setuptools import setup, find_packages
setup(
    name = "Windmill",
    version = "0.1",
    packages = find_packages(),

    install_requires = [
        'docutils>=0.3',
        'markdown',
        'mako',
        'pytz',
    ],

    setup_requires = [
    ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author = "William Wheatley",
    author_email = "will@iwill.id.au",
    description = "Windmill is a Site-Generation Utility",
    license = "BSD",
    keywords = "blog html website",
    url = "http://iwill.id.au/windmill/",   # project home page, if any
    zip_safe = True,

    entry_points = {
        'console_scripts': [
            'windmill = windmill.command:command',
            ],
        },
)
