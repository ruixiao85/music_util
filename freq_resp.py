
def valid_float(value: str, condition=lambda x: True) -> float:
  try:
    res=float(value)
    return res if condition(res) else None
  except:
    return None

import math
import binascii
class FreqResp(object):
  @staticmethod
  def sort_pair(_lst:list)->list:
    return sorted(_lst, key=lambda x: x[0]) # sort by 1st element (frequency)

  @staticmethod
  def resamp_fr(_raw_fr:list,_nr:int)->list:
    lf,lr=_raw_fr[0]; ef,er=_raw_fr[-1] # extract begin and end
    _raw_fr.insert(0,(min(10,lf-10),lr)); _raw_fr.append((max(21000,ef+1000),er)) # pad raw_fr
    lf,lr=_raw_fr[0] # last -> pad #0
    # print(f"raw freq resp with padding: {_raw_fr}")
    rn=len(_raw_fr); ri=1 # n of raw bands, raw idx start from 1
    _res_fr=[]; ci=0 # [0, 1, ...,  _nr-1] cur-idx
    while ri<rn and ci<_nr:
      cf=pow(1000.0,ci/(_nr-1))*20.0
      (rf,rr)=_raw_fr[ri]
      if cf<rf: # add
        logcf=math.log(cf/20.0,1000.0)
        lw,rw=math.fabs(math.log(lf/20.0,1000.0)-logcf),math.fabs(math.log(rf/20.0,1000.0)-logcf)
        cr=(lr*rw+rr*lw)/(lw+rw) # reversed weights to emphasize closer value
        # print(f"left {lf} : {lr} x {rw:.2f} right {rf} : {rr} x {lw:.2f} current {cf} : {cr:.2f}")
        _res_fr.append((cf,cr))
        ci+=1
      else:
        ri+=1
        lf,lr=rf,rr # try next set of fr
    _raw_fr.pop(0); _raw_fr.pop() # trim both ends of ref list
    # print(f"res freq resp: {_res_fr}")
    return _res_fr

  @staticmethod
  def to_csv(lst:list,csv:str,sep=','):
    with open(csv,'w') as f:
      f.write(f"frequency{sep}resp\n")
      for (cf,cr) in lst:
        f.write(f"{cf}{sep}{cr}\n")

  __slots__ = ['raw_fr','res_fr','nres'] # list of tuples (freq, resp)
  def __init__(self,_raw_fr:list=None,_res_fr:list=None,_nres:int=None):
    self.raw_fr=_raw_fr
    self.nres=_nres if _nres else 31
    self.res_fr=_res_fr if _res_fr else FreqResp.resamp_fr(_raw_fr,self.nres)

  @classmethod
  def from_csv(cls,csv:str,nr:int=None,sep=','):
    print(f"reading from {csv}")
    _raw_fr=[]
    with open(csv,'r') as f:
      for line in f:
        cols=line.split(sep)
        cf=valid_float(cols[0], lambda x: 20<=x<=20000) # current frequency
        if cf is not None: # freq valid
          cr=valid_float(cols[1], lambda x: -99<=x<=99) # current response
          if cr is not None: # resp valid
            _raw_fr.append((cf,cr))
    if nr==len(_raw_fr):
      return cls(None,_raw_fr,nr) # most likely preprocessed
    else:
      return cls(FreqResp.sort_pair(_raw_fr),None,nr) # resample needed

  @classmethod
  def res_adjust(cls,c:object,t:object):
    _res_adj=[]
    if len(c.res_fr)==len(t.res_fr): # same num of bands
      for idx,(cf,cr) in enumerate(c.res_fr): # current
        (tf,tr)=t.res_fr[idx] # target
        _res_adj.append((cf,tr-cr)) # skipped freq match check
      return cls(None,_res_adj)
    return None

  def raw_to_csv(self,csv:str,sep=','):
    if self.raw_fr:
      FreqResp.to_csv(self.raw_fr,f"{csv.rstrip('.csv')}_raw.csv",sep)

  def res_to_csv(self,csv:str,sep=','):
    FreqResp.to_csv(self.res_fr,f"{csv.rstrip('.csv')}_res.csv",sep)

  def res_to_xgeq(self,xgeq:str,ratio:float=1.0): # 31 bands graphic equalizaer
    rbands,nbands=31,len(self.res_fr) # required, num of available bands
    if rbands==nbands:
      limit=12
      prehex='66 6F 6F 5F 64 73 70 5F 78 67 65 71 0D 0A 31 0D 0A 76 3A 0C E7 A7 88 9F 41 A2 EA B0 0C 3A 9A C7 42 16 01 00 00 03 00 00 00 00 00 00 00 02 00 00 00'.replace(' ','')
      midhex='00 1F 00 00 00'.replace(' ','') # 4 bytes of global gain between pre and mid
      posthex='00 00 00 00 01 1F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'.replace(' ','')
      with open(f"{xgeq.rstrip('.xgeq')}~{round(ratio,1)}.xgeq","wb") as f:
        f.write(binascii.unhexlify(prehex))
        adjs=[adj*ratio for (fq,adj) in self.res_fr]
        mean=max(-1*limit,min(limit,sum(adjs)/len(adjs)))
        f.write((10*round(10*mean)).to_bytes(4,byteorder='little',signed=True))
        f.write(binascii.unhexlify(midhex))
        for adj in adjs:
          f.write((10*round(10*max(-1*limit,min(limit,adj-mean)))).to_bytes(4,byteorder='little',signed=True))
        f.write(binascii.unhexlify(posthex))
    else:
      print(f"cann't output for {nbands} bands != {rbands}")


if __name__ == "__main__":
  import os
  myHpType="onear"

  anchor="Sennheiser HD 800"
  # anchor="Sennheiser HD 800 S"
  if False:
    os.makedirs(anchor,exist_ok=True)
    # for sourceDir in ["headphonecom", "innerfidelity", "oratory1990"]:
    for sourceDir in ["innerfidelity", "oratory1990"]:
    # for sourceDir in [ "oratory1990"]:
      rootpath=f"AutoEq/measurements/{sourceDir}/data/{myHpType}"
      hpa=FreqResp.from_csv(f"{rootpath}/{anchor}/{anchor}.csv")
      for dirpath,dirnames,filenames in os.walk(rootpath):
        for dirname in dirnames:
          # print(dirpath,dirname)
          try:
            hpt=FreqResp.from_csv(f"{dirpath}/{dirname}/{dirname}.csv")
            # print(hpt.raw_fr); print(hpt.res_fr)
            hpd=FreqResp.res_adjust(hpa,hpt) # diff
            hpd.res_to_csv(f"{anchor}/{dirname}_{sourceDir}.csv")
          except: pass

  myHps=[
  # "AT897pos_innerfidelity_res",
  # "AT897pos_oratory1990_res",
  "AT897neg_innerfidelity_res",
  "AT897neg_oratory1990_res",
  # "AKG K701_innerfidelity_res",
  # "AKG K701_oratory1990_res",
  # "Audio-Technica ATH-W5000 2013_innerfidelity_res",
  # "Audio-Technica ATH-W5000_innerfidelity_res",
  # "Sennheiser HD 800_innerfidelity_res",
  # "Sennheiser HD 800_oratory1990_res",
  # "Sennheiser IE 800_oratory1990_res"
  ]
  for hp in myHps:
    hpc=FreqResp.from_csv(f"{anchor}/{hp}.csv")
    os.makedirs(f"{anchor}/{hp}",exist_ok=True)
    for dirpath,dirnames,filenames in os.walk(f"{anchor}"):
      for filename in filenames:
        if filename.endswith(".csv") and filename!=f"{hp}.csv":
          # print(dirpath,filename)
          hpt=FreqResp.from_csv(f"{anchor}/{filename}")
          hpd=FreqResp.res_adjust(hpc,hpt) # diff
          for ratio in [0.6,1.0]:
            hpd.res_to_xgeq(f"{anchor}/{hp}/{filename}.csv",ratio)

