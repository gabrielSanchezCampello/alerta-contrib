from setuptools import find_packages, setup

version = '5.3.1'

setup(
    name='assign_procedure',
    version=version,
    description='Alerta plugin for assign procedures to alerts',
    url='https://github.com/gabrielSanchezCampello/alerta-contrib',
    license='MIT',
    author='Nick Satterly',
    author_email='gabriel.sanchez.campello@gmail.com',
    packages=find_packages(),
    py_modules=['assign_procedure'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'classifyproc = assign_procedure:AssignProcedure'
        ]
    }
)
