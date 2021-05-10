import sys
import socket
import os
import shutil
import re
import time
from . import utils
from django.conf import settings


OKAPI = settings.OKAPI
HTML_FILTER = settings.HTML_FILTER


# Extract XLIFF from given document
def convert_file_to_xliff(filepath, content_type, source_language, target_language, out_filepath):
	global OKAPI, HTML_FILTER

	#Prepare conversion command depending on the document type
	if content_type in ["txt"]:
		cmd = "%s -seg -fc okf_plaintext -sl %s -tl %s -x %s" % (OKAPI, source_language, target_language, filepath)
	elif content_type in ["odt", "ods", "odp"]: #Open Office documents
		cmd = "%s -seg -fc okf_openoffice -sl %s -tl %s -x %s" % (OKAPI, source_language, target_language, filepath)
	elif content_type in ["xml", "wxml"]:
		cmd = "%s -seg -fc okf_xml -sl %s -tl %s -x %s" % (OKAPI, source_language, target_language, filepath)
	elif content_type in ["docx", "pptx", "xlsx"]: #Microsoft Office documents
		cmd = "%s -seg -fc okf_openxml -sl %s -tl %s -x %s" % (OKAPI, source_language, target_language, filepath)
	elif content_type in ["txlf", "xliff", "sdlxliff"]:
		shutil.copy(filepath, out_filepath)
		cmd = None
	elif content_type in ["html"]:
		utils.tidy_html(filepath)
		time.sleep(0.1) # Wait until resulting file has been closed
		cmd = "%s -seg -fc %s -sl %s -tl %s -x %s" % (OKAPI, HTML_FILTER, source_language, target_language, filepath)
	else:
		raise Exception("Content type not supported")

	if cmd:
		if utils.run_command(cmd) != 0:
			raise Exception("Error converting file to xliff. Please check logs")
		else:
			time.sleep(0.1) # Wait until resulting file has been closed
			shutil.copy(filepath + ".xlf", out_filepath)
			os.remove(filepath + ".xlf")
		
	if not os.path.exists(out_filepath):
		raise Exception("Output xliff file does not exist")


def convert_xliff_to_file(original_file, xliff_filepath, content_type, source_language, target_language, out_filepath):
	global OKAPI, HTML_FILTER

	shutil.copy(xliff_filepath, original_file + ".xlf")

	if content_type in ["odt", "ods", "odp"]: #Open Office documents
		cmd = "%s -seg -fc okf_openoffice -m %s -sl %s -ie utf8 -oe utf8 -overtrg" % (OKAPI, original_file + ".xlf", target_language)
	elif content_type in ["xml", "wxml"]:
		cmd = "%s -seg -fc okf_xml -m %s -sl %s -ie utf8 -oe utf8 -overtrg" % (OKAPI, original_file + ".xlf", target_language)
	elif content_type in ["docx", "pptx", "xlsx"]: # Microsoft Office documents
		cmd = "%s -seg -fc okf_openxml -m %s -sl %s -ie utf8 -oe utf8 -overtrg" % (OKAPI, original_file + ".xlf", target_language)
	elif content_type in ["txlf", "xliff", "sdlxliff"]:
		shutil.copy(xliff_filepath, original_file + ".done")
		cmd = None
	elif content_type in ["html"]:
		cmd = "%s -seg -fc %s -m %s -sl %s -ie utf8 -oe utf8 -overtrg" % (OKAPI, HTML_FILTER, original_file + ".xlf", target_language)
	else:
		raise Exception("Content type not supported")

	if cmd:
		if utils.run_command(cmd) != 0:
			raise Exception("Error converting xliff to file. Please check logs")
		else:
			time.sleep(0.1) # Wait until resulting file has been closed
			filename, extension = os.path.splitext(original_file)
			#Command returns "original_filename.out.extension" file
			shutil.copy(filename + ".out" + extension, original_file + ".done")

	if content_type in ["html"]:
		# Convert html to htmlstring if necessary
		print("CHECKING HTML IF STRING")
		utils.convert_html_to_htmlstring(original_file + ".original", original_file + ".done", out_filepath)
	else:
		shutil.copy(original_file + ".done", out_filepath)
		
	if not os.path.exists(out_filepath):
		raise Exception("Output xliff file does not exist")



def extract_targets_from_xliff(xliff_filepath):
	xliff_file = open(xliff_filepath, "r", encoding="utf-8")
	content = xliff_file.read()

	counter=1
	targets = []
	while True:
		match = re.search(r"<target[^>]*>((?!<<__@\d+__>>)(.|\s)*?)</target>", content)
		if match:
			targets.append(match.group(1))
			span = match.span(1)
			content = content[:span[0]] + "<<__@"+str(counter)+"__>>" + content[span[1]:]
			counter += 1
		else:
			break

	return content, targets


def extract_translatable_segments(targets):
	all_segments = []

	for target in targets:

		mrk_tags = re.findall(r"(<mrk[^>]*>)((.|\s)*?)</mrk>", target)

		# <mrk> tag is used to break down the content of the <target> into smaller runs of text (for example, sentences)
		if mrk_tags:		
			for mrk in mrk_tags:
				# Remove <ph>, <ept> and <bpt> tags as they contain no translatable inner text
				mrk_ = re.sub(r"<ph[^>]*>(.|\s)*?</ph>", "", mrk[1])
				mrk_ = re.sub(r"<ept[^>]*>(.|\s)*?</ept>", "", mrk_)
				mrk_ = re.sub(r"<bpt[^>]*>(.|\s)*?</bpt>", "", mrk_)

				# Segment on <x/>, <bx/> and <ex/>. These tags do not contain text inside and represent style. Therefore, text can be segmented at these tags.
				segments = []
				tags = re.findall('(<(x|bx|ex)[^>]*>)', mrk_)
				if tags:
					for tag in tags:
						segment, rest = mrk_.split(tag[0])
						if segment:
							segments.append(segment)
						segments.append(("<<__@tag__>>", tag[0]))
						mrk_ = rest
					if rest:
						segments.append(rest)
				else:
					segments.append(mrk_)

				all_segments.extend(segments)

			all_segments.append(("<<__@trg__>>", mrk[0]))

		else:
			all_segments.append(target)
			all_segments.append(("<<__@trg__>>", '<mrk mid="0" mtype="seg">'))

	return all_segments


def extract_text_only(segments):
	untagged_segments = []
	for segment in segments:
		if not isinstance(segment, tuple):
			no_tags = utils.removeTags(segment).strip()
			untagged_segments.append(no_tags)
	return untagged_segments


def recover_segmentation(original_segments, untagged_segments, translated_segments):
		result = []
		for s in original_segments:
			if not isinstance(s, tuple):
				result.append([s, untagged_segments[0], translated_segments[0]])
				translated_segments.pop(0)
				untagged_segments.pop(0)
			else:
				result.append(s)

		assert len(translated_segments) == 0 and len(untagged_segments) == 0
		
		return result

def recover_targets_from_segmentation(segments):
	targets = []
	temp = ""
	for segment in segments:
		if isinstance(segment, tuple):
			if segment[0] == "<<__@tag__>>":
				temp += segment[1]
			elif segment[0] == "<<__@trg__>>":
				targets.append(segment[1] + temp.strip() + "</mrk>")
				temp = ""
		else:
			temp += " " + segment
	return targets


def insert_segments_in_xliff(replaced_xliff, segments, result_xliff_filepath):
	out_file = open(result_xliff_filepath,"w", encoding="utf-8")

	for i,line in enumerate(segments):
		replaced_xliff = re.sub("<<__@"+str(i+1)+"__>>", line, replaced_xliff)

	out_file.write(replaced_xliff)
	out_file.close()

	if not os.path.exists(result_xliff_filepath):
		raise Exception("There was an error inserting segments in xliff")