#!/bin/env python
from pathlib import Path
import os
limit=12
nbands=31
bands=[20,25,31.5,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,
  1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000,20000] # 31 Graphic Equalizer

def parse_integer(value: str, default: int=0) -> int:
  try:
    return round(float(value),0)
  except ValueError:
    return default

def band_left(folder: str, ext: str=".csv")-> []:
  files=[f for f in os.listdir(folder) if f.endswith(ext)]
  print(files[0])
  with open(folder+os.path.sep+files[0]) as f:
    ad=[0]*len(bands) # adjustment list
    lf,lv=0,0 # last frequency (Hz), last value (dB)
    bi=0 # band index
    for line in f:
      cols=line.split(',')
      cf=parse_integer(cols[0]) # current frequency
      cv=parse_integer(cols[1]) # current value
      if lf<bands[bi]<=cf:
        # print(f'{line}\tfreq{cf}\tval{cv}')
        ad[bi]=lv; bi+=1
      if bi>=len(bands):
        break
      lf=cf; lv=cv
  return ad

# round(log(fq/20.0,base=2**0.3333)) in [0,1,...,30]
import math
def freq_int_wt(fq:float)->(int,float):
  fi=math.log(fq/20.0,2**0.33333); fir=round(fi)
  if 0<=fir<=30: return (fir,1.0-abs(fir-fi))
  return (None,0)
def band_int_round(folder: str, ext: str=".csv")-> []:
  files=[f for f in os.listdir(folder) if f.endswith(ext)]
  print(files[0])
  iw_map={}
  with open(folder+os.path.sep+files[0]) as f:
    for line in f:
      cols=line.split(',')
      cf=parse_integer(cols[0],999999) # current frequency
      ci,cw=freq_int_wt(cf) # current index, weight
      if ci is not None: # valid index
        cv=parse_integer(cols[1]) # current value
        lv,lw=iw_map.get(ci,(0,0))
        lv+=cv; lw+=cw
        iw_map[ci]=(lv,lw)
  # print(iw_map)
  ad=[0]*nbands
  for i in range(nbands):
    if i in iw_map:
      cv,cw=iw_map[i]
      ad[i]=cv/cw
  return ad

# get_freq_resp=band_left
get_freq_resp=band_int_round

def clean_name(file: str)-> str:
  return file.replace("-","").replace(" ","").lower()

import binascii
prehex='66 6F 6F 5F 64 73 70 5F 78 67 65 71 0D 0A 31 0D 0A 76 3A 0C E7 A7 88 9F 41 A2 EA B0 0C 3A 9A C7 42 16 01 00 00 03 00 00 00 00 00 00 00 02 00 00 00 00 00 00 00 00 1F 00 00 00'.replace(' ','')
posthex='00 00 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'.replace(' ','')

# myHps=["Audio-Technica ATH-W5000","Sennheiser HD 600", "Sennheiser HD 800","AKG K701"]
# myHps=["Audio-Technica ATH-W5000"]
myHps=["Sennheiser HD 800","AKG K701"]
myHpsClean=[clean_name(hp) for hp in myHps]
# myBrands=["AKG"]
myBrands=["Audio-Technica","Audeze","AKG","Beyerdynamic","Bose","Bowers","Denon","E-Mu","Focal","Fostex","Grado","HiFiMAN",
  "Massdrop","Meze","Monoprice","Monster","MrSpeakers","Oppo","Pioneer","Polk","Sennheiser","Shure","Sony","Stax","Ultrasone","ZMF"]
myBrandsClean=[clean_name(b) for b in myBrands]
for sourceDir in ["headphonecom", "innerfidelity", "oratory1990"]:
  for dirpath,dirnames,filenames in os.walk(f"{sourceDir}/data/onear"):
    hpsFoundClean=[clean_name(hp) for hp in dirnames]
    for hpc in myHps:
      if clean_name(hpc) in hpsFoundClean:
        try: os.mkdir(f'{sourceDir}~{hpc}'.replace(" ",""))
        except OSError as e: pass
        fc=get_freq_resp(f"{sourceDir}/data/onear/{hpc}")
        print(fc)
        for hpt in dirnames:
          if clean_name(hpt.split(" ")[0]) in myBrandsClean and clean_name(hpt) not in myHpsClean:
            ft=get_freq_resp(f"{sourceDir}/data/onear/{hpt}")
            for ratio in [0.6,1.0]:
              with open(f'{sourceDir}~{hpc}/{hpt}~{ratio}.xgeq'.replace(" ",""),"wb") as f:
                f.write(binascii.unhexlify(prehex))
                for a,b in zip(fc,ft):
                  adj=round(10*max(-1*limit,min(limit,(b-a)*ratio)))*10
                  f.write((adj).to_bytes(4,byteorder='little',signed=True))
                f.write(binascii.unhexlify(posthex))
                  # f.write(f'{max(-1*limit,min(limit,round((b-a)*ratio)))}\n')
            # exit(1) # debug one case
