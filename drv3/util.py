# -*- coding: utf-8 -*-

################################################################################
# Copyright © 2016-2017 BlackDragonHunt
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To But It's Not My Fault Public
# License, Version 1, as published by Ben McGinnes. See the COPYING file
# for more details.
################################################################################

import io
import os
import zlib
import struct

class BinaryHelper(object):
  
  def get_u32(self):
    return to_u32(self.read(4))
  
  def get_u16(self):
    return to_u16(self.read(2))
  
  def get_u8(self):
    return to_u8(self.read(1))
  
  def get_u32be(self):
    return to_u32be(self.read(4))
  
  def get_u16be(self):
    return to_u16be(self.read(2))
  
  def get_s32(self):
    return to_s32(self.read(4))
  
  def get_s16(self):
    return to_s16(self.read(2))
  
  def get_s8(self):
    return to_s8(self.read(1))
  
  def get_s32be(self):
    return to_s32be(self.read(4))
  
  def get_s16be(self):
    return to_s16be(self.read(2))
  
  def get_bin(self, length):
    return BinaryData(self.read(length))
  
  def get_str(self, encoding = "utf-8"):
    bytes = bytearray()
    
    while True:
      if encoding == "utf-16" or encoding == "unicode":
        ch = self.read(2)
        if ch[0] == 0 and ch[1] == 0:
          break
        else:
          bytes.append(ch[0])
          bytes.append(ch[1])
      else:
        ch = self.read(1)
        if ch[0] == 0:
          break
        else:
          bytes.append(ch[0])
    
    string = bytes.decode(encoding)
    print(string)
    return string

class BinaryFile(io.BufferedReader, BinaryHelper):
  pass

class BinaryData(io.BytesIO, BinaryHelper):
  pass

def to_u32(b):
  return struct.unpack("<I", b)[0]

def to_u16(b):
  return struct.unpack("<H", b)[0]

def to_u8(b):
  return struct.unpack("<B", b)[0]

def to_u32be(b):
  return struct.unpack(">I", b)[0]

def to_u16be(b):
  return struct.unpack(">H", b)[0]

def to_s32(b):
  return struct.unpack("<i", b)[0]

def to_s16(b):
  return struct.unpack("<h", b)[0]

def to_s8(b):
  return struct.unpack("<b", b)[0]

def to_s32be(b):
  return struct.unpack(">i", b)[0]

def to_s16be(b):
  return struct.unpack(">h", b)[0]

def from_u32(b):
  return struct.pack("<I", b)

def from_u16(b):
  return struct.pack("<H", b)

def from_u8(b):
  return struct.pack("<B", b)

def from_u32be(b):
  return struct.pack(">I", b)

def from_u16be(b):
  return struct.pack(">H", b)

def list_all_files(dirname):
  
  if not os.path.isdir(dirname):
    return

  for item in os.listdir(dirname):
    full_path = os.path.join(dirname, item)
  
    if os.path.isfile(full_path):
      yield full_path
      
    elif os.path.isdir(full_path):
      for filename in list_all_files(full_path):
        yield filename

def zlib_inflate(data):
  decompress = zlib.decompressobj(
          # -zlib.MAX_WBITS  # see above
  )
  inflated = decompress.decompress(data)
  inflated += decompress.flush()
  return inflated

def reverse_enum(L):
  for index in reversed(xrange(len(L))):
    yield index, L[index]

### EOF ###
