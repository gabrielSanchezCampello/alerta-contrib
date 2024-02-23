from setuptools import find_packages, setup

version = '5.3.1'

setup(
    name='alert2jira',
    version=version,
    description='Alerta plugin for send alerts to differents jira',
    url='https://github.com/gabrielSanchezCampello/alerta-contrib',
    license='',
    author='Gabriel Sanchez',
    author_email='gabriel.sanchez.campello@gmail.com',
    packages=find_packages(),
    py_modules=['alert2jira'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'alert2jira = alert2jira:Alert2jira'
        ]
    }
)
