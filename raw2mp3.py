#!/usr/bin/env python3
# coding: utf-8

import sys
import os
import shutil

# from: https://gist.github.com/bancek/b37b780292540ed2d17d assume cue and target file in the same dir
def parse_cue(cue_file, outdir):
  cue_dir = os.path.dirname(cue_file)
  d = open(cue_file).read().splitlines()

  general = {}
  tracks = []
  current_file = None

  for line in d:
    if line.startswith('REM GENRE '):
      general['genre'] = ' '.join(line.split(' ')[2:]).replace('"', '')
    if line.startswith('REM DATE '):
      general['date'] = ' '.join(line.split(' ')[2:])
    if line.startswith('PERFORMER '):
      general['artist'] = ' '.join(line.split(' ')[1:]).replace('"', '')
    if line.startswith('TITLE '):
      general['album'] = ' '.join(line.split(' ')[1:]).replace('"', '')
    if line.startswith('FILE '):
      current_file = ' '.join(line.split(' ')[1:-1]).replace('"', '')

    if line.startswith('  TRACK '):
      track = general.copy()
      track['track'] = int(line.strip().split(' ')[1], 10)

      tracks.append(track)

    if line.startswith('    TITLE '):
      tracks[-1]['title'] = ' '.join(line.strip().split(' ')[1:]).replace('"', '')
    if line.startswith('    PERFORMER '):
      tracks[-1]['artist'] = ' '.join(line.strip().split(' ')[1:]).replace('"', '')
    if line.startswith('    INDEX 01 '):
      #t = map(int, ' '.join(line.strip().split(' ')[2:]).replace('"', '').split(':'))
      t = [int(a) for a in ' '.join(line.strip().split(' ')[2:]).replace('"', '').split(':')]
      tracks[-1]['start'] = 60 * t[0] + t[1] + t[2] / 100.0

  for i in range(len(tracks)):
    if i != len(tracks) - 1:
      tracks[i]['duration'] = tracks[i + 1]['start'] - tracks[i]['start']

  cmds = []
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
    cmd += ' -i "%s"' % os.path.join(cue_dir,current_file)
    cmd += ffmpeg_setting
    cmd += ' -ss %.2d:%.2d:%.2d' % (track['start'] / 60 / 60, track['start'] / 60 % 60, int(track['start'] % 60))
    if 'duration' in track:
      cmd += ' -t %.2d:%.2d:%.2d' % (track['duration'] / 60 / 60, track['duration'] / 60 % 60, int(track['duration'] % 60))
    cmd += ' ' + ' '.join('-metadata %s="%s"' % (k, v) for (k, v) in metadata.items())
    # filename = '%s-%s-%.2d.mp3' % (track['artist'].replace(":", "-"), track['title'].replace(":", "-"), track['track'])
    filename = '%s %.2d. %s.mp3' % (track['album'], track['track'], track['title'].replace(":", "-"))
    cmd += ' "%s"' % os.path.join(outdir, filename)
    cmds.append(cmd)

  return cmds

def print_run(cmd):
  print(cmd)
  os.system(cmd)

def convert_cue(incue, outdir):
  cmds = parse_cue(incue, outdir)
  for cmd in cmds:
    print_run(cmd)

def convert_onefile(infile, outdir):
  filename = os.path.basename(infile)
  name, ext = os.path.splitext(filename)
  cmd = '%s' % ffmpeg_path
  cmd += ffmpeg_setting
  cmd = ' -i "%s"' % infile
  cmd += ' "%s.mp3"' % os.path.join(outdir, name)
  print_run(cmd)
def process_dir(indir, outdir):
  for root, dirs, files in os.walk(indir): # resursive search
    cues = [f for f in files if f.endswith(".cue")]
    if cues: # process cue if any, skip other types
      for cue in cues:
        convert_cue(os.path.join(root, cue), outdir)
    else: # no cue file
      for f in files:
        name, ext = os.path.splitext(f)
        if ext in ext2convert:
          convert_onefile(os.path.join(root, f), outdir)
        elif ext in ext0convert:
          os.link(os.path.join(root, f), os.path.join(outdir, f))
          # shutil.copy2(os.path.join(root, f), os.path.join(outdir, f))


ext2convert=("flac", "ape", "m4a", "oga")
ext0convert=("mp3", "wma", "ogg", "txt", "jpg", "gif")
ffmpeg_setting=" -q:a 1 " # -q:a 0=220~260 1=190~250 2=170~210

if "__main__" == __name__:
  ffmpeg_path=sys.argv[1]
  indirfile = sys.argv[2]
  if len(sys.argv) > 3:
    outdir = sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
  else:
    outdir = ""

  if os.path.isdir(indirfile):
    process_dir(indirfile, outdir)
  elif indirfile.endswith(".cue"):
    convert_cue(indirfile, outdir)
  else:
    convert_onefile(indirfile, outdir)