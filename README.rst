vctools
=======

This is a simple library for using Visual Studio command line tools from Python. 

Principle of operation:

1. Scan *VSXXXCOMNTOOLS* environment variables.
2. Run script *%VSXXXCOMNTOOLS%\\VC\\vcvarsall.bat* and load environment variables installed form it.
3. Run command line utilities using environment variables loaded in the previous step.

Usage
-----

.. code:: python

  import vctools

  # load environment variables from Visual Studio 2015 for amd64 platform
  # (platform list see in script vcvarsall.bat)
  tools = vctools.VCTools(version_name='2015', platform='amd64')
  # find and load environment variables from latest installed Visual Studio
  # for x86 platform
  tools = vctools.VCTools()

  # compile main.cpp to main.exe
  tools.cl('main.cpp')

  # different operations compile and link
  tools.cl(['/c', 'foo.cpp', 'main.cpp'])
  tools.ml(['/c', 'bar.asm'])
  tools.lib(['foo.obj', 'bar.obj', '/OUT:utils.lib'])
  tools.link(['main.obj', 'utils.lib', '/OUT:main.exe'])

  # run nmake
  tools.nmake()

  # run msbuild
  tools.msbuild()

  # run devenv
  tools.devenv()

  # run any command
  tools.check_call(['dumpbin', 'main.exe'])

  # run over subprocess.check_call
  import subprocess
  subprocess.check_call(['editbin', 'main.exe', '/STACK:4096'], env=tools.environ, shell=True)

To usage over command line see *python vc.py -h*

License
-------

MIT License. See the LICENSE file.
