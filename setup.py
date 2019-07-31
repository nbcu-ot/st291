from distutils.core import setup
setup(
  name='st291',
  packages=['st291'],
  version='0.0.1',
  license='apache-2.0',
  description='Decode ST291 binary into a human-understandable terminology',
  author='Dhurv Garg',
  author_email='dhurv.garg@nbcuni.com',
  url='https://github.com/abcd/st291',
  download_url='https://github.com/abcd/st291/archive/v0.0.1.tar.gz',
  keywords=['smpte', 'scte104', 'transport', 'stream', 'broadcast', 'uncompressed', 'video'],
  install_requires=[
          'bitstring'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Multimedia',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
  ],
)
