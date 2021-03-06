from distutils.core import setup

setup(
    name='remove-bg',
    packages=['removebg'],
    version='0.2.1',
    license='MIT',
    description='Client for remove.bg with extra features.',
    author='retxxxirt',
    author_email='retxxirt@gmail.com',
    url='https://github.com/retxxxirt/removebg',
    keywords=['removebg', 'remove.bg', 'remove background'],
    install_requires=['requests==2.23.0', 'beautifulsoup4==4.8.2',
                      'python-anticaptcha==0.4.2', 'tempmail-client==0.1.2']
)
