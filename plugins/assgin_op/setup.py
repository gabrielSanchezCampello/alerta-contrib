from setuptools import find_packages, setup

version = '1.0.0'

setup(
    name='assign_op',
    version=version,
    description='Alerta plugin for assign procedures to alerts',
    url='https://github.com/gabrielSanchezCampello/alerta-contrib',
    license='',
    author='Gabriel Sanchez',
    author_email='gabriel.sanchez.campello@gmail.com',
    packages=find_packages(),
    py_modules=['assign_op'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'assign_op = assign_op:AssignOperator'
        ]
    }
)
