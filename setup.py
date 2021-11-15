
from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name="alerta-rpi_daemon",
    version=version,
    description='Alerta plugin to check online status',
    url='https://github.com/matmoscicki/alerta-rpi_daemon',
    license='MIT',
    author='Mateusz Moscicki',
    author_email='mat.moscicki@gmail.com',
    packages=find_packages(),
    py_modules=['alerta_rpi_daemon', 'rpi_daemon_client'],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'rpi_daemon = alerta_rpi_daemon:RpiDaemonCheck'
        ]
    }
)
