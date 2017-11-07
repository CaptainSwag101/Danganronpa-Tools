﻿################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import io
import os

from util import *
from drv3_dec import *

SPC_MAGIC   = "CPS."
TABLE_MAGIC = "Root"

def spc_ex(filename, out_dir = None):
  out_dir = out_dir or os.path.splitext(filename)[0]
  f = BinaryFile(open(filename, "rb"))
  spc_ex_data(f, filename, out_dir)
  f.close()

def spc_ex_data(f, filename, out_dir):
  
  try:
    os.makedirs(out_dir)
  except:
    pass
  
  magic = f.read(4).decode()
  
  if magic == "$CMP":
    dec = srd_dec_data(f)
    f.close()
    f = BinaryData(dec)
    magic = f.read(4).decode()
  
  if not magic == SPC_MAGIC:
    f.close()
    print("Invalid SPC file.")
    return
  
  unk1 = f.read(0x24)
  file_count = f.get_u32()
  unk2 = f.get_u32()
  f.read(0x10)
  
  table_magic = f.read(4).decode()
  f.read(0x0C)
  
  if not table_magic == TABLE_MAGIC:
    f.close()
    print("Invalid SPC file.")
    return
  
  for i in range(file_count):
    cmp_flag = f.get_u16()
    unk_flag = f.get_u16()
    cmp_size = f.get_u32()
    dec_size = f.get_u32()
    name_len = f.get_u32() + 1 # Null terminator excluded from count.
    f.read(0x10) # Padding?
    
    # Everything's aligned to multiples of 0x10.
    name_padding = (0x10 - name_len % 0x10) % 0x10
    data_padding = (0x10 - cmp_size % 0x10) % 0x10
    
    # We don't actually want the null byte though, so pretend it's padding.
    fn = f.read(name_len - 1).decode()
    f.read(name_padding + 1)
    
    #print()
    #print(cmp_flag, unk_flag, cmp_size, dec_size)
    #print(fn)
    
    data = f.read(cmp_size)
    f.read(data_padding)
    
    # Uncompressed.
    if cmp_flag == 0x01:
      pass
    
    # Compressed.
    elif cmp_flag == 0x02:
      data = spc_dec(data)
      
      if not len(data) == dec_size:
        print("Size mismatch:", dec_size, len(data))
    
    # Load from an external file.
    elif cmp_flag == 0x03:
      ext_file = filename + "_" + fn
      data = srd_dec(ext_file)
    
    else:
      raise Exception(fn + ": Unknown SPC compression flag 0x%02X" % cmp_flag)
    
    if os.path.splitext(fn)[1].lower() == ".spc":
      subfile = os.path.join(out_dir, fn)
      spc = BinaryData(data)
      spc_ex_data(spc, subfile, subfile)
    
    else:
      with open(os.path.join(out_dir, fn), "wb") as out:
        out.write(data)
        
  f.close()

if __name__ == "__main__":
  dirs = [
    # Vita retail
    "partition_data_vita",
    "partition_resident_vita",
    "partition_patch101_vita",
    "partition_patch102_vita",
    
    # Vita demo
    "partition_data_vita_taiken_ja",
    "partition_resident_vita_taiken_ja",
    
    # PC retail
    "partition_data_win",
    "partition_data_win_us",
    "partition_data_win_jp",
    "partition_resident_win",
    
    # PC demo
    "partition_data_win_demo",
    "partition_data_win_demo_us",
    "partition_data_win_demo_jp",
    "partition_resident_win_demo",
  ]
  
  for dirname in dirs:
    for fn in list_all_files(dirname):
      if not os.path.splitext(fn)[1].lower() == ".spc":
        continue
      
      out_dir = os.path.splitext(os.path.join("dec", fn))[0]
      
      print(fn)
      spc_ex(fn, out_dir)

### EOF ###
