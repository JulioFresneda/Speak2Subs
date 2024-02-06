from setuptools import setup, find_packages

setup(
    name='Speak2Subs',
    version='1.3',
    packages=find_packages(),
    install_requires=[
        "moviepy",
        "jiwer",
        "pandas",
        "pydub",
        "noisereduce",
        "art"
    ],
    entry_points={
        'console_scripts': [
            'speak2subs = Speak2Subs.cli:main',
        ],
    },

    author='Julio Antonio Fresneda Garcia',
    author_email='julioantonio.fresnedagarcia@gmail.com',
    description='TFM',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_package',
    project_urls={

    },
    classifiers=[

    ]
)
