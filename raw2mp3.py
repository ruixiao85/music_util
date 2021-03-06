#!/usr/bin/env python3

import sys
import os

from pathlib import Path
def make_dir(target):
  _dir=os.path.dirname(target)
  print(f"making directory to [{_dir}]")
  Path(_dir).mkdir(parents=True, exist_ok=True)
  return {'f':target, 'd':_dir}

# import subprocess
def print_run(cmd):
  print(cmd)
  os.system(cmd)
  # subprocess.call(cmd)

def convert_cue(indir, subpath, outdir):
  general = {}
  tracks = []
  cue_file, audio_file = os.path.join(indir, subpath), None
  for line in open(cue_file).read().splitlines():
    if line.startswith('REM GENRE '):
      general['genre'] = ' '.join(line.split(' ')[2:]).replace('"', '')
    elif line.startswith('REM DATE '):
      general['date'] = ' '.join(line.split(' ')[2:])
    elif line.startswith('PERFORMER '):
      general['artist'] = ' '.join(line.split(' ')[1:]).replace('"', '')
    elif line.startswith('TITLE '):
      general['album'] = ' '.join(line.split(' ')[1:]).replace('"', '')
    elif line.startswith('FILE '):
      audio_file = ' '.join(line.split(' ')[1:-1]).replace('"', '')
    elif line.startswith('  TRACK '):
      track = general.copy()
      track['track'] = int(line.strip().split(' ')[1], 10)
      tracks.append(track)
    elif line.startswith('    TITLE '):
      tracks[-1]['title'] = ' '.join(line.strip().split(' ')[1:]).replace('"', '')
    elif line.startswith('    PERFORMER '):
      tracks[-1]['artist'] = ' '.join(line.strip().split(' ')[1:]).replace('"', '')
    elif line.startswith('    INDEX 01 '):
      #t = map(int, ' '.join(line.strip().split(' ')[2:]).replace('"', '').split(':'))
      t = [int(a) for a in ' '.join(line.strip().split(' ')[2:]).replace('"', '').split(':')]
      tracks[-1]['start'] = 60 * t[0] + t[1] + t[2] / 100.0

  for i in range(len(tracks)):
    if i != len(tracks) - 1:
      tracks[i]['duration'] = tracks[i + 1]['start'] - tracks[i]['start']

  for track in tracks:
    metadata = {
      'artist': track['artist'],
      'title': track['title'],
      'album': track['album'],
      'track': str(track['track']) + '/' + str(len(tracks))
    }
    if 'genre' in track: metadata['genre'] = track['genre']
    if 'date' in track: metadata['date'] = track['date']
    cmd = ffmpeg_path
    cmd += ' -i "%s"' % os.path.join(os.path.dirname(cue_file),audio_file)
    cmd += ffmpeg_set
    cmd += ' -ss %.2d:%.2d:%.2d' % (track['start'] / 60 / 60, track['start'] / 60 % 60, int(track['start'] % 60))
    if 'duration' in track:
      cmd += ' -t %.2d:%.2d:%.2d' % (track['duration'] / 60 / 60, track['duration'] / 60 % 60, int(track['duration'] % 60))
    cmd += ' ' + ' '.join('-metadata %s="%s"' % (k, v) for (k, v) in metadata.items())
    outsubdir = make_dir(os.path.join(outdir, subpath))['d']
    basename = '%s %.2d. %s' % (track['album'], track['track'], track['title'].replace(":", "-"))
    cmd += ' "%s%s"' % (os.path.join(outsubdir, basename), ffmpeg_ext)
    print_run(cmd)

def convert_onefile(indir, subpath, outdir):
  cmd = '%s' % ffmpeg_path
  cmd += ffmpeg_set
  cmd = ' -i "%s"' % os.path.join(indir, subpath)
  cmd += ' "%s%s"' % (make_dir(os.path.splitext(os.path.join(outdir, subpath))[0])['f'], ffmpeg_ext)
  print_run(cmd)

def link_onefile(indir, subpath, outdir):
  # os.link(os.path.join(indir, subpath), make_dir(os.path.join(outdir, subpath))['f'])
  os.system(f"ln -f {os.path.join(indir, subpath)} {make_dir(os.path.join(outdir, subpath))['f']}") # force overwrite

import shutil
def copy_onefile(indir, subpath, outdir):
  shutil.copy2(os.path.join(indir, subpath), make_dir(os.path.join(outdir, subpath))['f'])

ext2keep=(".txt", ".jpg", ".jpeg", ".gif")
ext0convert=(".mp3", "m4a", ".wma", ".ogg", ".oga")
ext2convert=(".flac", ".ape", ".wav", ".tta")
ffmpeg_set,ffmpeg_ext=" -acodec libmp3lame -aq 1",".mp3" # -q:a 0=220~260 1=190~250 2=170~210
# ffmpeg_set,ffmpeg_ext=" -acodec libmp3lame -b:a 160k",".mp3" # max at 320K
# ffmpeg_set,ffmpeg_ext=" -c:a libfdk_aac -vbr 5",".m4a" # -vbr 1=20-32 2=32-40 3=48-56 4=64-72 5=96-112
# ffmpeg_set,ffmpeg_ext=" -c:a aac -b:a 160k",".m4a" # -vbr 1=20-32 2=32-40 3=48-56 4=64-72 5=96-112

if "__main__" == __name__:
  ffmpeg_path=sys.argv[1]
  indir = sys.argv[2]
  outdir = sys.argv[3]

  for root, dirs, files in os.walk(indir): # resursive search
    subdir=os.path.relpath(root, indir)
    for f in files:
      subpath=os.path.join(subdir, f)
      name, ext = os.path.splitext(f)
      # print(f"subdir [{subdir}] name [{name}] ext [{ext}]")
      if ext == '.cue':
        print(f"convert cue [{f}]"); convert_cue(indir, subpath, outdir)
      elif ext in ext2keep:
        # print(f"copy file [{f}]")#; copy_onefile(indir, subpath, outdir)
        print(f"link file [{f}]")#; link_onefile(indir, subpath, outdir)
      elif name+'.cue' not in files: # assume cue and audio file share base name
        if ext in ext2convert:
          print(f"convert file [{f}]"); convert_onefile(indir, subpath, outdir)
        elif ext in ext0convert:
          # print(f"copy file [{f}]")#; copy_onefile(indir, subpath, outdir)
          print(f"link file [{f}]")#; link_onefile(indir, subpath, outdir)

