#!/bin/env python
from pathlib import Path
import os
bands=[55,77,110,156,220,311,440,622,880,1200,1800,2500,3500,5000,7000,10000,14000,20000]
# static const double bands[] = {
  # 65.406392,92.498606,130.81278,184.99721,261.62557,369.99442,523.25113,
  # 739.9884 ,1046.5023,1479.9768,2093.0045,2959.9536,4186.0091,5919.9072,
  # 8372.0181,11839.814,16744.036
# };
limit=20

def parse_integer(value: str, default: int=0) -> int:
  try:
    return round(float(value),0)
  except ValueError:
    return default

def get_freq_resp(folder: str, ext: str=".csv")-> []:
  files=[f for f in os.listdir(folder) if f.endswith(ext)]
  print(files[0])
  with open(folder+os.path.sep+files[0]) as f:
    ad=[0]*len(bands) # adjustment list
    lf,lv=0,0 # last frequency (Hz), last value (dB)
    bi=0 # band index
    for line in f:
      cols=line.split(',')
      cf=parse_integer(cols[0]) # current freqeuncy
      cv=parse_integer(cols[1]) # current value
      if lf<bands[bi]<=cf:
        # print(f'{line}\tfreq{cf}\tval{cv}')
        ad[bi]=lv; bi+=1
      if bi>=len(bands):
        break
      lf=cf; lv=cv
  return ad

def clean_name(file: str)-> str:
  return file.replace("-","").replace(" ","").lower()

myHps=["Audio-Technica ATH-W5000","Sennheiser HD 600", "Sennheiser HD 800","AKG K701"]
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
