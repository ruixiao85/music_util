#!/bin/env python
from pathlib import Path
import os
limit=20
nbands=18
bands=[55,77,110,156,220,311,440,622,880,1200,1800,2500,3500,5000,7000,10000,14000,20000] # display

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

# round(log(fq/55,base=1.414)) in [0,1,...,nbands-1]
import math
def freq_int_wt(fq:float)->(int,float):
  fi=math.log(fq/55.0,1.414); fir=round(fi)
  if 0<=fir<nbands: return (fir,1.0-abs(fir-fi))
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

# myHps=["Audio-Technica ATH-W5000","Sennheiser HD 600", "Sennheiser HD 800","AKG K701"]
# myHps=["Audio-Technica ATH-W5000"]
myHps=["Sennheiser HD 800","AKG K701"]
myHpsClean=[clean_name(hp) for hp in myHps]
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
              with open(f'{sourceDir}~{hpc}/{hpt}~{ratio}.feq'.replace(" ",""),"w") as f:
                for a,b in zip(fc,ft):
                  f.write(f'{max(-1*limit,min(limit,round((b-a)*ratio)))}\n')
            # exit(1) # debug one case
