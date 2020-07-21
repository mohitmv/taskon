from setuptools import setup

import taskon

about = 'Taskon is a task runner used for execution of interdependnt tasks'

setup(
	name='taskon',
	version = "1.0.0",
	url='https://github.com/mohitmv/taskon',
	author='Mohit Saini',
	author_email='mohitsaini1196@gmail.com',
	description=about,
	long_description=about,
	packages=["taskon"],
	install_requires=[],
	extras_require={}, 
	classifiers=[
		'Programming Language :: Python :: 3',
	],
	entry_points={}
)

