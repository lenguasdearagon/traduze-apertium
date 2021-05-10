import subprocess as sp
import shlex
import re
from . import xliff
import time
import shutil

def run_command(command, std_input=None, std_output=None):
    print("[COMMAND]", command)
    stdin = sp.PIPE
    if std_input:
        stdin = std_input
    stdout = sp.PIPE
    if std_output:
        stdout = std_output
    process = sp.Popen(shlex.split(command), stdin=stdin, stdout=stdout)
    while True:
        if not std_output:
            output = process.stdout.readline()
            if output:
                print(output.strip().decode())
        if process.poll() is not None:
            break

    rc = process.poll()
    return rc

def tidy_html(filepath):
    shutil.copy(filepath, filepath + ".original")
    cmd = "tidy --wrap 0 -f %s.tidy_errors.txt -m %s" % (filepath, filepath)
    run_command(cmd)

def removeTags(line):
    line = re.sub("<[^>]+>","",line)
    line = re.sub(" +"," ",line).strip()
    return line

def word_count(filepath, content_type, source_language="es", target_language="ar"):
    print("=======================")
    print("= Document word count =")
    print("=======================")

    # Extract XLIFF file from original document
    xliff.convert_file_to_xliff(filepath, content_type, source_language, target_language, filepath + ".xliff")
    # Extract translatable segments from XLIFF file
    xliff_content_replaced, targets = xliff.extract_targets_from_xliff(filepath + ".xliff")
    translatable_segments_tagged = xliff.extract_translatable_segments(targets)
    translatable_segments = xliff.extract_text_only(translatable_segments_tagged)

    text = re.sub(r"\n", " ", " ".join(translatable_segments))
    text = re.sub(r"\s+", " ", text)
    words = len(text.split())

    return words