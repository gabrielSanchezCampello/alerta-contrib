from setuptools import find_packages, setup

version = '5.3.1'

setup(
    name='alert2teams',
    version=version,
    description='Alerta plugin for send alerts to differents teams',
    url='https://github.com/gabrielSanchezCampello/alerta-contrib',
    license='',
    author='Gabriel Sanchez',
    author_email='gabriel.sanchez.campello@gmail.com',
    packages=find_packages(),
    py_modules=['alert2teams'],
    install_requires=['pymsteams'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'classifyproc = alert2teams:Alert2Teams'
        ]
    }
)
