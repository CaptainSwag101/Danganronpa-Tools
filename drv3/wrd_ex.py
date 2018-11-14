# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

from util import *

def wrd_ex(filename, out_file = None):

  out_file = out_file or os.path.splitext(filename)[0] + ".txt"
  f = BinaryFile(filename, "rb")
  text = wrd_ex_data(f)
  f.close()

  if not text:
    return

  out_dir = os.path.dirname(out_file)

  try:
    os.makedirs(out_dir)
  except:
    pass

  with open(out_file, "wb") as f:
    if text:
      f.write("########## Text ##########\n\n")
      for string in text:
        f.write(string.encode("UTF-8"))
        f.write("\n\n")

def wrd_ex_data(f):

  str_count       	= f.get_u16()
  label_count     	= f.get_u16()
  param_count 	  	= f.get_u16()
  sublabel_count  	= f.get_u16() # Some labels are broken into smaller sections
  unk 			  	= f.get_u32() # Padding?

  # idk
  sublabel_off_ptr	= f.get_u32() # Pointer to sublabel offset table
  label_off_ptr     = f.get_u32() # Pointer to label offset table
  label_name_ptr   	= f.get_u32() # Pointer to plaintext label name list
  param_ptr   		= f.get_u32() # Pointer to plaintext parameter list
  str_ptr    		= f.get_u32() # Pointer to plaintext string list

  # Code section.
  code = bytearray(f.read(sublabel_off_ptr - 0x20))
  
  
  # Plaintext parameters.
  params = []
  f.seek(param_ptr)
  for i in xrange(param_count):
    param_len = f.get_u8() + 1
    param = f.get_str(bytes_per_char = 1, encoding = "UTF-8")
    params.append(param)
  
  
  # Dialogue strings.
  strs = []

  # Text is stored externally.
  if str_ptr == 0:
    return None


  f.seek(str_ptr)
  for i in xrange(str_count):
    str_len = f.get_u8()

    # ┐(´∀｀)┌
    if str_len >= 0x80:
      str_len += (f.get_u8() - 1) * 0x80

    str = f.get_str(bytes_per_char = 2, encoding = "UTF-16LE")
    strs.append(str)


  # Put it all together.
  lines = wrd_parse(code)
  text  = []
  used  = set()

  for speaker, line in lines:
    used.add(line)
    line = strs[line]
    speaker = params[speaker]

    if speaker:
      line = u"[%s]\n%s" % (speaker, line)

    text.append(line)

  for i in xrange(len(strs)):
    if not i in used:
      text.append(u"[UNUSED]\n" + strs[i])
	  
  return text

def wrd_parse(data):

  lines   = []
  speaker = -1
  p       = 0
  data_len = len(data)

  # We need a minimum of four bytes for a nametag or a text display command.
  while p <= data_len - 4:
    b = data[p]
    p += 1

    if not b == 0x70:
      continue

    cmd = data[p]
    p += 1

    if cmd == 0x46:
      line = to_u16be(data[p : p + 2])
      lines.append((speaker, line))
      p += 2

    elif cmd == 0x1D:
      speaker = to_u16be(data[p : p + 2])
      p += 2

  return lines

if __name__ == "__main__":
  dirs = [
    # Vita retail
    "dec/partition_data_vita",
    "dec/partition_resident_vita",
    "dec/partition_patch101_vita",
    "dec/partition_patch102_vita",

    # Vita demo
    "dec/partition_data_vita_taiken_ja",
    "dec/partition_resident_vita_taiken_ja",

    # PC retail
    "dec/partition_data_win",
    "dec/partition_data_win_us",
    "dec/partition_data_win_jp",
    "dec/partition_resident_win",

    # PC demo
    "dec/partition_data_win_demo",
    "dec/partition_data_win_demo_us",
    "dec/partition_data_win_demo_jp",
    "dec/partition_resident_win_demo",
  ]

  for dirname in dirs:
    for fn in list_all_files(dirname):
      if not os.path.splitext(fn)[1].lower() == ".wrd":
        continue

      out_dir, basename = os.path.split(fn)
      out_dir  = dirname + "-ex" + out_dir[len(dirname):]
      out_file = os.path.join(out_dir, os.path.splitext(basename)[0] + ".txt")

      try:
        os.makedirs(out_dir)
      except:
        pass

      print fn
      wrd_ex(fn, out_file)

### EOF ###
