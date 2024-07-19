# -*- coding: utf-8 -*-
import os

all_dirs = []
def show_files(path):
	file_list = os.listdir(path)
	for file in file_list:
		cur_path = os.path.join(path, file)
		if os.path.isdir(cur_path):
			all_dirs.append(cur_path)
			if "@eaDir" in cur_path:
				continue
			else:
				show_files(cur_path)
		else:
			continue
	return all_dirs

dir_path = "/volume2/Media"
contents = show_files(dir_path)
for content in contents:
	if "@eaDir" in content:
		print(content
)	#os.system('rm -rf "'+content+'"')