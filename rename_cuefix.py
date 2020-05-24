from pathlib import Path
import os
import re
import fileinput
import codecs

rg=".专辑[\\.]{1,2}\([A-Za-z]{3,4}\)"
fl="FILE .+ WAVE"

def rename_file(filename:str):
  res=re.search(rg,filename)
  if res:
    phrase=res.group()
    if input(f"file rename: remove {phrase} from {filename}? n to skip").lower().startswith('n'):
      print("user skipped")
    else:
      os.rename(filename,filename.replace(phrase,"")); print("renamed")
  # else:
    # print(f"{filename} don't match existing patterns for removal.")

import subprocess
def check_cue(filename:str):
  encodings = ['utf-8', 'gbk', 'windows-1250', 'windows-1252', ]
  for e in encodings:
    try:
      fi=codecs.open(filename, 'r', encoding=e)
      content=fi.read(); fi.close()
      break
    except UnicodeDecodeError:
      pass
  if not content:
    print(f'encoding error {filename}')
    # p = subprocess.Popen(["notepad.exe", filename])
    return
  fls=re.search(fl,content)
  if fls:
    target_file=fls.group().split('\"')[1]
    target=os.path.join(os.path.dirname(filename),target_file)
    if not os.path.exists(target):
      res=re.search(rg,target_file)
      if res:
        phrase=res.group(); print(phrase)
        if os.path.exists(os.path.join(os.path.dirname(filename),target_file.replace(phrase,""))):
          ncontent=content.replace(phrase,"")
          fo=open(filename, 'w', encoding='utf-8')
          fo.write(ncontent); fo.close()
          print(f"problem fixed by removing {phrase} from {filename}")
      else:
        print(f'{target} not found')
        pe=subprocess.Popen(f'explorer.exe {os.path.dirname(filename)}')
        # pe=subprocess.Popen(f'explorer /select, {os.path.dirname(filename)}')
        # pn=subprocess.Popen(["notepad.exe", filename])
        # pe=subprocess.Popen(["explorer.exe", filename])
        pe.wait()
        # pn.wait()
        # exit_codes = [p.wait() for p in pn,pe]
  else:
    print(f"FILE statement not found in {filename}")
  # fo=open(filename, 'w', encoding='utf-8-sig')

wd="F:\\Music\\"

# for filepath in Path(wd).rglob('*'):
  # filename=str(filepath)
  # if "专辑" in filename:
    # rename_file(filename)

for filepath in Path(wd).rglob('*.cue'):
  filename=str(filepath)
  check_cue(filename)