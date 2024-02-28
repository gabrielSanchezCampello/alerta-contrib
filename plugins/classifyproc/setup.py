from setuptools import find_packages, setup

version = '2.1.0'

setup(
    name='process_alert',
    version=version,
    description='Alerta plugin for assign procedures to alerts',
    url='https://github.com/gabrielSanchezCampello/alerta-contrib',
    license='',
    author='Gabriel Sanchez',
    author_email='gabriel.sanchez.campello@gmail.com',
    packages=find_packages(),
    py_modules=['process_alert'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'process_alert = process_alert:ProcessAlert'
        ]
    }
)
