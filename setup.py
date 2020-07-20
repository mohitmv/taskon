
from setuptools import setup


import taskon

setup(
	name='taskon',
	version = "1.0.0",
	url='https://github.com/mohitmv/taskon',
	author='Mohit Saini',
	author_email='mohitsaini1196@gmail.com',
	description='Super easy task runner for interdependnt tasks',
	long_description='Super easy task runner for interdependnt tasks',
	packages=["taskon"],
	install_requires=[],
	extras_require={}, 
	classifiers=[
		'Programming Language :: Python :: 3',
	],
	entry_points={}
)

