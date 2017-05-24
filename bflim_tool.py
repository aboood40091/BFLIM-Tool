#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BFLIM Tool
# Version 1.1
# Copyright © 2017 AboodXD

# This file is part of BFLIM Tool.

# BFLIM Tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# BFLIM Tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""bflim_tool.py: The main executable."""

import os, sys, struct, time
import requests
import shutil
from tkinter import Tk, Frame, Button, Canvas, Scrollbar, Menu
from tkinter.filedialog import askopenfilename, askdirectory
import tkinter.messagebox as messagebox
import urllib.request
import warnings
import zipfile

top = Tk()
canvas = Canvas(top)
frame = Frame(canvas)
menubar = Menu(top)
filemenu = Menu(menubar, tearoff=0)

formats = {0x01: 'GX2_SURFACE_FORMAT_TC_R8_UNORM',
           0x07: 'GX2_SURFACE_FORMAT_TC_R8_G8_UNORM',
           0x08: 'GX2_SURFACE_FORMAT_TCS_R5_G6_B5_UNORM',
           0x1a: 'GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_UNORM',
           0x31: 'GX2_SURFACE_FORMAT_T_BC1_UNORM',
           0x32: 'GX2_SURFACE_FORMAT_T_BC2_UNORM',
           0x33: 'GX2_SURFACE_FORMAT_T_BC3_UNORM',
           0x34: 'GX2_SURFACE_FORMAT_T_BC4_UNORM',
           0x35: 'GX2_SURFACE_FORMAT_T_BC5_UNORM'}

BCn_formats = [0x31, 0x431, 0x32, 0x432, 0x33, 0x433, 0x34, 0x35]

formats2 = {0x01: 'L8',
            0x07: 'L8A8',
            0x08: 'R5G6B5 / RGB565',
            0x1a: 'ARGB8 / ABGR8',
            0x31: 'BC1 / DXT1',
            0x32: 'BC2 / DXT3',
            0x33: 'BC3 / DXT5',
            0x34: 'BC4U / ATI1',
            0x35: 'BC5U / ATI2'}

formatHwInfo = b"\x00\x00\x00\x01\x08\x03\x00\x01\x08\x01\x00\x01\x00\x00\x00\x01" \
    b"\x00\x00\x00\x01\x10\x07\x00\x00\x10\x03\x00\x01\x10\x03\x00\x01" \
    b"\x10\x0B\x00\x01\x10\x01\x00\x01\x10\x03\x00\x01\x10\x03\x00\x01" \
    b"\x10\x03\x00\x01\x20\x03\x00\x00\x20\x07\x00\x00\x20\x03\x00\x00" \
    b"\x20\x03\x00\x01\x20\x05\x00\x00\x00\x00\x00\x00\x20\x03\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x01\x20\x03\x00\x01\x00\x00\x00\x01" \
    b"\x00\x00\x00\x01\x20\x0B\x00\x01\x20\x0B\x00\x01\x20\x0B\x00\x01" \
    b"\x40\x05\x00\x00\x40\x03\x00\x00\x40\x03\x00\x00\x40\x03\x00\x00" \
    b"\x40\x03\x00\x01\x00\x00\x00\x00\x80\x03\x00\x00\x80\x03\x00\x00" \
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x10\x01\x00\x00" \
    b"\x10\x01\x00\x00\x20\x01\x00\x00\x20\x01\x00\x00\x20\x01\x00\x00" \
    b"\x00\x01\x00\x01\x00\x01\x00\x00\x00\x01\x00\x00\x60\x01\x00\x00" \
    b"\x60\x01\x00\x00\x40\x01\x00\x01\x80\x01\x00\x01\x80\x01\x00\x01" \
    b"\x40\x01\x00\x01\x80\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

class FLIMData():
    data = b''

class FLIMHeader(struct.Struct):
    def __init__(self):
        super().__init__('>4s2H2IH2B')

    def data(self, data, pos):
        (self.magic,
        self.endian,
        self.size_,
        self._08,
        self.fileSize,
        self._10,
        self._12,
        self._13) = self.unpack_from(data, pos)

class imagHeader(struct.Struct):
    def __init__(self, bom):
        super().__init__(bom + '4sI3H2BI')

    def data(self, data, pos):
        (self.magic,
        self.infoSize,
        self.width,
        self.height,
        self.alignment,
        self.format_,
        self.swizzle,
        self.imageSize) = self.unpack_from(data, pos)

def surfaceGetBitsPerPixel(surfaceFormat):
    hwFormat = surfaceFormat & 0x3F
    bpp = formatHwInfo[hwFormat * 4 + 0]
    return bpp

def DDStoBFLIM(flim, dds, f):
    with open(f, "rb") as inf:
        inb = inf.read()
        inf.close()

    name = os.path.splitext(dds)[0]

    os.system('C:/Tex/TexConv2.exe -i "' + dds + '" -o "' + name + '.gtx"')

    swizzle = (flim.swizzle & 0xFFF) >> 8
    format_ = flim.format

    os.system('C:/Tex/TexConv2.exe -i "' + name + '.gtx" -f ' + formats[format_] + ' -tileMode GX2_TILE_MODE_2D_TILED_THIN1 -swizzle ' + str(swizzle) + ' -o "' + name + '2.gtx"')

    os.remove(name + '.gtx')

    with open(name + '2.gtx', "rb") as gfd1:
        gfd = gfd1.read()
        gfd1.close()

    if inb[-0x28:-0x24] != b"FLIM":
        messagebox.showinfo("", "Invalid BFLIM header!")
        os.remove(name + '2.gtx')

    elif gfd[:4] != b"Gfx2":
        messagebox.showinfo("", "Invalid GTX header!")
        os.remove(name + '2.gtx')

    elif ((gfd[0x60:0x64] != flim.imageSize.to_bytes(4, 'big')) or (gfd[0x60:0x64] != gfd[0xF0:0xF4])):
        messagebox.showinfo("", "Data size mismatch")
        os.remove(name + '2.gtx')

    elif gfd[0x54:0x58] != flim.format.to_bytes(4, 'big'):
        messagebox.showinfo("", "Format mismatch")
        os.remove(name + '2.gtx')

    else:
        inb = bytearray(inb)

        inb[:flim.imageSize] = gfd[0xFC:0xFC+flim.imageSize]

        with open(f, "wb") as output:
            output.write(inb)
            output.close()

        os.remove(name + '2.gtx')

        messagebox.showinfo("", "Done!")

def openfolder():
    folder = askdirectory(parent=top)

    for file in os.listdir(folder):
        if file.endswith(".bflim"):
            filename = folder + "/" + file

            with open(filename, "rb") as inf:
                inb = inf.read()
                inf.close()

            global menubar
            global filemenu
            
            flim = FLIMData()

            pos = struct.unpack(">I", inb[-4:])[0]

            header = FLIMHeader()
            header.data(inb, pos)
                
            if header.magic != b"FLIM":
                messagebox.showinfo("", "Invalid BFLIM header!")
            else:
                if header.endian == 0xFEFF:
                    bom = '>'
                elif header.endian == 0xFFFE:
                    bom = '<'

                pos += header.size

                info = imagHeader(bom)
                info.data(inb, pos)

                if info.magic != b'imag':
                    messagebox.showinfo("", "Invalid imag header!")
                else:
                    flim.width = info.width
                    flim.height = info.height

                    if info.format_ == 0x00:
                        flim.format = 0x01
                    elif info.format_ == 0x01:
                        flim.format = 0x01
                    elif info.format_ == 0x03:
                        flim.format = 0x07
                    elif info.format_ == 0x05:
                        flim.format = 0x08
                    elif info.format_ == 0x09:
                        flim.format = 0x1a
                    elif info.format_ == 0x0C:
                        flim.format = 0x31
                    elif info.format_ == 0x0D:
                        flim.format = 0x32
                    elif info.format_ == 0x0E:
                        flim.format = 0x33
                    elif info.format_ == 0x0F:
                        flim.format = 0x34
                    elif info.format_ == 0x10:
                        flim.format = 0x34
                    elif info.format_ == 0x11:
                        flim.format = 0x35
                    elif info.format_ == 0x12:
                        flim.format = 0x31
                    elif info.format_ == 0x14:
                        flim.format = 0x1a
                    elif info.format_ == 0x15:
                        flim.format = 0x31
                    elif info.format_ == 0x16:
                        flim.format = 0x32
                    elif info.format_ == 0x17:
                        flim.format = 0x33
                    else:
                        flim.format = 0

                    if flim.format == 0:
                        pass
                    else:
                        flim.imageSize = info.imageSize

                        flim.swizzle = info.swizzle
                        flim.swizzle = (((flim.swizzle & 0xF0) >> 4) // 2) << 8

                        flim.alignment = info.alignment

                        # Calculate Pitch
                        # Welp, does this even work?
                        bpp = surfaceGetBitsPerPixel(flim.format)

                        try:
                            if (flim.format != 0x31 and flim.format != 0x32 and flim.format != 0x33):
                                size = flim.width
                            else:
                                size = flim.height

                            flim.pitch = size // bpp

                            import math
                            frac, whole = math.modf(flim.pitch)
                            whole = int(whole)

                            while (bpp * whole) < size:
                                whole += 1

                            flim.pitch = (bpp * whole)
                        except ZeroDivisionError:
                            flim.pitch = 1

                        flim.data = inb[:info.imageSize]

                        name = os.path.splitext(filename)[0]

                        if os.path.isfile(name + ".dds"):
                            pass
                        else:
                            head1 = bytearray.fromhex("4766783200000020000000070000000100000002000000000000000000000000424C4B7B0000002000000001000000000000000B0000009C0000000000000000")
                            head2 = bytearray.fromhex("424C4B7B0000002000000001000000000000000C") + flim.imageSize.to_bytes(4, 'big') + bytearray.fromhex("0000000000000000")
                            head3 = bytearray.fromhex("424C4B7B00000020000000010000000000000001000000000000000000000000")

                            info = bytearray(0x9C)

                            info[:4] = (1).to_bytes(4, 'big')
                            info[4:8] = flim.width.to_bytes(4, 'big')
                            info[8:0xC] = flim.height.to_bytes(4, 'big')
                            info[0xC:0x10] = (1).to_bytes(4, 'big')
                            info[0x10:0x14] = (1).to_bytes(4, 'big')
                            info[0x14:0x18] = flim.format.to_bytes(4, 'big')
                            info[0x18:0x1C] = (0).to_bytes(4, 'big')
                            info[0x1C:0x20] = (1).to_bytes(4, 'big')
                            info[0x20:0x24] = flim.imageSize.to_bytes(4, 'big')
                            info[0x24:0x28] = (0).to_bytes(4, 'big')
                            info[0x28:0x2C] = (0).to_bytes(4, 'big')
                            info[0x2C:0x30] = (0).to_bytes(4, 'big')
                            info[0x30:0x34] = (4).to_bytes(4, 'big')
                            info[0x34:0x38] = flim.swizzle.to_bytes(4, 'big')
                            info[0x38:0x3C] = flim.alignment.to_bytes(4, 'big')
                            info[0x3C:0x40] = flim.pitch.to_bytes(4, 'big')
                            info[0x40:0x4D] = bytearray(0xD)
                            info[0x4D:0x78] = bytearray(0x2B)
                            info[0x78:0x7C] = (1).to_bytes(4, 'big')
                            info[0x7C:0x80] = (0).to_bytes(4, 'big')
                            info[0x80:0x84] = (1).to_bytes(4, 'big')
                            info[0x84:0x88] = (0x10203).to_bytes(4, 'big')
                            info[0x88:0x9C] = bytearray(0x14)

                            file = head1 + info + head2 + flim.data + head3

                            with open(name + "2.gtx", "wb") as output:
                                output.write(file)
                                output.close()

                            print("")
                            os.system('C:/Tex/TexConv2.exe -i "' + name + '2.gtx" -f GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_UNORM -o "' + name + '.gtx"')
                            os.system('C:/Tex/gtx_extract.exe "' + name + '.gtx"')

                            try:
                                os.remove(name + '.gtx')
                            except FileNotFoundError:
                                os.system('C:/Tex/TexConv2.exe -i "' + name + '2.gtx" -o "' + name + '.dds"')

                                if os.path.isfile(name + '.dds'):
                                    if flim.format == 0x01:
                                        format_ = 61
                                    elif flim.format == 0x07:
                                        format_ = 49
                                    elif flim.format == 0x08:
                                        format_ = 85
                                    elif flim.format == 0x1a:
                                        format_ = 28
                                    elif flim.format == 0x31:
                                        format_ = "BC1"
                                    elif flim.format == 0x32:
                                        format_ = "BC2"
                                    elif flim.format == 0x33:
                                        format_ = "BC3"
                                    elif flim.format == 0x34:
                                        format_ = "BC4U"
                                    elif flim.format == 0x35:
                                        format_ = "BC5U"

                                    hdr = writeHeader(1, flim.width, flim.height, format_, flim.format in BCn_formats)

                                    with open(name + ".dds", "rb") as output:
                                        out = bytearray(output.read())
                                        output.close()

                                    with open(name + ".dds", "wb") as output:
                                        out[:0x80] = hdr
                                        output.write(out)
                                        output.close()

                            os.remove(name + '2.gtx')

    messagebox.showinfo("", "Done!")

def openfile():
    options = {}
    options['filetypes'] = [('BFLIM files', '.bflim')]
    filename = askopenfilename(parent=top, filetypes=options['filetypes'])

    with open(filename, "rb") as inf:
        inb = inf.read()
        inf.close()

    global menubar
    global filemenu
    
    flim = FLIMData()

    pos = struct.unpack(">I", inb[-4:])[0]

    header = FLIMHeader()
    header.data(inb, pos)
        
    if header.magic != b"FLIM":
        messagebox.showinfo("", "Invalid BFLIM header!")
    else:
        if header.endian == 0xFEFF:
            bom = '>'
        elif header.endian == 0xFFFE:
            bom = '<'

        pos += header.size

        info = imagHeader(bom)
        info.data(inb, pos)

        if info.magic != b'imag':
            messagebox.showinfo("", "Invalid imag header!")
        else:
            flim.width = info.width
            flim.height = info.height

            if info.format_ == 0x00:
                flim.format = 0x01
            elif info.format_ == 0x01:
                flim.format = 0x01
            elif info.format_ == 0x03:
                flim.format = 0x07
            elif info.format_ == 0x05:
                flim.format = 0x08
            elif info.format_ == 0x09:
                flim.format = 0x1a
            elif info.format_ == 0x0C:
                flim.format = 0x31
            elif info.format_ == 0x0D:
                flim.format = 0x32
            elif info.format_ == 0x0E:
                flim.format = 0x33
            elif info.format_ == 0x0F:
                flim.format = 0x34
            elif info.format_ == 0x10:
                flim.format = 0x34
            elif info.format_ == 0x11:
                flim.format = 0x35
            elif info.format_ == 0x12:
                flim.format = 0x31
            elif info.format_ == 0x14:
                flim.format = 0x1a
            elif info.format_ == 0x15:
                flim.format = 0x31
            elif info.format_ == 0x16:
                flim.format = 0x32
            elif info.format_ == 0x17:
                flim.format = 0x33
            else:
                flim.format = 0

            if flim.format == 0:
                messagebox.showinfo("", "Unsupported format!")
            else:
                flim.imageSize = info.imageSize

                flim.swizzle = info.swizzle
                flim.swizzle = (((flim.swizzle & 0xF0) >> 4) // 2) << 8

                flim.alignment = info.alignment

                # Calculate Pitch
                # Welp, does this even work?
                bpp = surfaceGetBitsPerPixel(flim.format)

                try:
                    if (flim.format != 0x31 and flim.format != 0x32 and flim.format != 0x33):
                        size = flim.width
                    else:
                        size = flim.height

                    flim.pitch = size // bpp

                    import math
                    frac, whole = math.modf(flim.pitch)
                    whole = int(whole)

                    while (bpp * whole) < size:
                        whole += 1

                    flim.pitch = (bpp * whole)
                except ZeroDivisionError:
                    flim.pitch = 1

                flim.data = inb[:info.imageSize]

                scr = Scrollbar(top, orient="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scr.set)

                scr.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True)
                canvas.create_window((4,4), window=frame, anchor="nw")

                frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

                options['filetypes'] = [('DDS files', '.dds')]

                name = os.path.splitext(filename)[0]

                ugh = False

                if os.path.isfile(name + ".dds"):
                    pass
                else:
                    head1 = bytearray.fromhex("4766783200000020000000070000000100000002000000000000000000000000424C4B7B0000002000000001000000000000000B0000009C0000000000000000")
                    head2 = bytearray.fromhex("424C4B7B0000002000000001000000000000000C") + flim.imageSize.to_bytes(4, 'big') + bytearray.fromhex("0000000000000000")
                    head3 = bytearray.fromhex("424C4B7B00000020000000010000000000000001000000000000000000000000")

                    info = bytearray(0x9C)

                    info[:4] = (1).to_bytes(4, 'big')
                    info[4:8] = flim.width.to_bytes(4, 'big')
                    info[8:0xC] = flim.height.to_bytes(4, 'big')
                    info[0xC:0x10] = (1).to_bytes(4, 'big')
                    info[0x10:0x14] = (1).to_bytes(4, 'big')
                    info[0x14:0x18] = flim.format.to_bytes(4, 'big')
                    info[0x18:0x1C] = (0).to_bytes(4, 'big')
                    info[0x1C:0x20] = (1).to_bytes(4, 'big')
                    info[0x20:0x24] = flim.imageSize.to_bytes(4, 'big')
                    info[0x24:0x28] = (0).to_bytes(4, 'big')
                    info[0x28:0x2C] = (0).to_bytes(4, 'big')
                    info[0x2C:0x30] = (0).to_bytes(4, 'big')
                    info[0x30:0x34] = (4).to_bytes(4, 'big')
                    info[0x34:0x38] = flim.swizzle.to_bytes(4, 'big')
                    info[0x38:0x3C] = flim.alignment.to_bytes(4, 'big')
                    info[0x3C:0x40] = flim.pitch.to_bytes(4, 'big')
                    info[0x40:0x4D] = bytearray(0xD)
                    info[0x4D:0x78] = bytearray(0x2B)
                    info[0x78:0x7C] = (1).to_bytes(4, 'big')
                    info[0x7C:0x80] = (0).to_bytes(4, 'big')
                    info[0x80:0x84] = (1).to_bytes(4, 'big')
                    info[0x84:0x88] = (0x10203).to_bytes(4, 'big')
                    info[0x88:0x9C] = bytearray(0x14)

                    file = head1 + info + head2 + flim.data + head3

                    with open(name + "2.gtx", "wb") as output:
                        output.write(file)
                        output.close()

                    print("")
                    os.system('C:/Tex/TexConv2.exe -i "' + name + '2.gtx" -f GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_UNORM -o "' + name + '.gtx"')
                    os.system('C:/Tex/gtx_extract.exe "' + name + '.gtx"')

                    try:
                        os.remove(name + '.gtx')
                    except FileNotFoundError:
                        os.system('C:/Tex/TexConv2.exe -i "' + name + '2.gtx" -o "' + name + '.dds"')

                        if os.path.isfile(name + '.dds'):
                            if flim.format == 0x01:
                                format_ = 61
                            elif flim.format == 0x07:
                                format_ = 49
                            elif flim.format == 0x08:
                                format_ = 85
                            elif flim.format == 0x1a:
                                format_ = 28
                            elif flim.format == 0x31:
                                format_ = "BC1"
                            elif flim.format == 0x32:
                                format_ = "BC2"
                            elif flim.format == 0x33:
                                format_ = "BC3"
                            elif flim.format == 0x34:
                                format_ = "BC4U"
                            elif flim.format == 0x35:
                                format_ = "BC5U"

                            hdr = writeHeader(1, flim.width, flim.height, format_, flim.format in BCn_formats)

                            with open(name + ".dds", "rb") as output:
                                out = bytearray(output.read())
                                output.close()

                            with open(name + ".dds", "wb") as output:
                                out[:0x80] = hdr
                                output.write(out)
                                output.close()
                        else:
                            messagebox.showinfo("Whoops", "Something went wrong!")
                            ugh = True

                    os.remove(name + '2.gtx')

                if not ugh:
                    tv = 'Replace "' + os.path.basename(name) + '"\n' + formats2[flim.format]
                    b = Button(frame, text=tv, command=lambda flim=flim : DDStoBFLIM(flim, askopenfilename(parent=top, filetypes=options['filetypes']), filename))
                    b.pack(padx=1, pady=1)
                    
                    menubar.destroy()
                    filemenu.destroy()

                    messagebox.showinfo("", "Done!")
                else:
                    scr.destroy()

# ----------\/-DDS writer-\/---------- #

# Copyright © 2016-2017 AboodXD

# Supported formats:
#  -RGBA8
#  -RGB10A2
#  -RGB565
#  -RGB5A1
#  -RGBA4
#  -L8
#  -L8A8
#  -L4A4
#  -BC1_UNORM
#  -BC2_UNORM
#  -BC3_UNORM
#  -BC4_UNORM
#  -BC4_SNORM
#  -BC5_UNORM
#  -BC5_SNORM

# Feel free to include this in your own program if you want, just give credits. :)

def writeHeader(num_mipmaps, w, h, format_, compressed):
    hdr = bytearray(128)

    if format_ == 28: # RGBA8
        fmtbpp = 4
        has_alpha = 1
        rmask = 0x000000ff
        gmask = 0x0000ff00
        bmask = 0x00ff0000
        amask = 0xff000000

    elif format_ == 85: # RGB565
        fmtbpp = 2
        has_alpha = 0
        rmask = 0x0000001f
        gmask = 0x000007e0
        bmask = 0x0000f800
        amask = 0x00000000

    elif format_ == 61: # L8
        fmtbpp = 1
        has_alpha = 0
        rmask = 0x000000ff
        gmask = 0x000000ff
        bmask = 0x000000ff
        amask = 0x00000000

    elif format_ == 49: # L8A8
        fmtbpp = 2
        has_alpha = 1
        rmask = 0x000000ff
        gmask = 0x000000ff
        bmask = 0x000000ff
        amask = 0x0000ff00

    flags = (0x00000001) | (0x00001000) | (0x00000004) | (0x00000002)

    caps = (0x00001000)

    if num_mipmaps == 0: num_mipmaps = 1
    if num_mipmaps != 1:
        flags |= (0x00020000)
        caps |= ((0x00000008) | (0x00400000))

    if not compressed:
        flags |= (0x00000008)

        if (fmtbpp == 1 or format_ == 49): # LUMINANCE
            pflags = (0x00020000)

        else: # RGB
            pflags = (0x00000040)

        if has_alpha != 0:
            pflags |= (0x00000001)

        size = w * fmtbpp

    else:
        flags |= (0x00080000)
        pflags = (0x00000004)

        if format_ == "BC1":
            fourcc = b'DXT1'
        elif format_ == "BC2":
            fourcc = b'DXT3'
        elif format_ == "BC3":
            fourcc = b'DXT5'
        elif format_ == "BC4U":
            fourcc = b'BC4U'
        elif format_ == "BC5U":
            fourcc = b'BC5U'

        size = ((w + 3) >> 2) * ((h + 3) >> 2)
        if (format_ == "BC1" or format_ == "BC4U"):
            size *= 8
        else:
            size *= 16

    hdr[:4] = b'DDS '
    hdr[4:4+4] = 124 .to_bytes(4, 'little')
    hdr[8:8+4] = flags.to_bytes(4, 'little')
    hdr[12:12+4] = h.to_bytes(4, 'little')
    hdr[16:16+4] = w.to_bytes(4, 'little')
    hdr[20:20+4] = size.to_bytes(4, 'little')
    hdr[28:28+4] = num_mipmaps.to_bytes(4, 'little')
    hdr[76:76+4] = 32 .to_bytes(4, 'little')
    hdr[80:80+4] = pflags.to_bytes(4, 'little')

    if compressed:
        hdr[84:84+4] = fourcc
    else:
        hdr[88:88+4] = (fmtbpp << 3).to_bytes(4, 'little')
        hdr[92:92+4] = rmask.to_bytes(4, 'little')
        hdr[96:96+4] = gmask.to_bytes(4, 'little')
        hdr[100:100+4] = bmask.to_bytes(4, 'little')
        hdr[104:104+4] = amask.to_bytes(4, 'little')

    hdr[108:108+4] = caps.to_bytes(4, 'little')

    return hdr

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

def main():
    global tex
    global scr

    print("(C) 2017 AboodXD")

    down = False

    files = ["C:/Tex/gfd.dll", "C:/Tex/gtx_extract.exe", "C:/Tex/TexConv2.exe", "C:/Tex/texUtils.dll"]

    if not os.path.isfile("C:/Tex/new.txt"):
        down = True
    else:
        for file in files:
            if not os.path.isfile(file):
                down = True
        with open("C:/Tex/new.txt", "r") as txt:
            if txt.read() != 'v3.1':
                down = True

    if down:
        warnings.filterwarnings("ignore")

        print("")
        print("Downloading the necessary tools...")

        if not os.path.isdir("C:\Tex"):
            os.mkdir("C:\Tex")

        print("")
        print("Fetching GTX Extractor (C ver.)... ")
        print("")
        response = requests.get('https://github.com/aboood40091/RandomStuff/', verify=False)

        if (int(response.status_code)) == 200:
            print("Connected to the download page!")

        else:
            response = requests.get('https://www.google.com', verify=False)
            if (int(response.status_code)) == 200:
                print("")
                print("It seems that the download page is down. Try restarting BFLIM Tool and check if it still doesn't work.")
                print("")
                print("Exiting in 5 seconds...")
                time.sleep(5)
                sys.exit(1)

            else:
                print("")
                print("It looks like you don't have a working internet connection. Connect to another network, or solve the connection problem.")
                print("")
                print("Exiting in 5 seconds...")
                time.sleep(5)
                sys.exit(1)

        source = "gtx_extract.exe"
        destination = "C:/Tex"

        if os.path.isfile(destination + '/' + source):
            os.remove(destination + '/' + source)

        print("")
        print("Downloading...")
        urllib.request.urlretrieve("https://github.com/aboood40091/RandomStuff/releases/download/v0.1/gtx_extract_no5.exe", "gtx_extract.exe")
        print("Download completed!")

        print("")
        print("Moving files...")
        
        if not os.path.isfile(destination + '/' + source):
            shutil.move(source, destination)

        print("")
        print("Fetching TexConv2... ")
        print("")
        response = requests.get('https://github.com/aboood40091/WiiUTools/tree/master/TexHaxU', verify=False)

        if (int(response.status_code)) == 200:
            print("Connected to the download page!")

        else:
            response = requests.get('https://www.google.com', verify=False)
            if (int(response.status_code)) == 200:
                print("")
                print("It seems that the download page is down. Try restarting BFLIM Tool and check if it still doesn't work.")
                print("")
                print("Exiting in 5 seconds...")
                time.sleep(5)
                sys.exit(1)

            else:
                print("")
                print("It looks like you don't have a working internet connection. Connect to another network, or solve the connection problem.")
                print("")
                print("Exiting in 5 seconds...")
                time.sleep(5)
                sys.exit(1)

        source1 = "gfd.dll"
        source2 = "TexConv2.exe"
        source3 = "texUtils.dll"
        destination = "C:/Tex"

        if os.path.isfile(destination + '/' + source1):
            os.remove(destination + '/' + source1)

        if os.path.isfile(destination + '/' + source2):
            os.remove(destination + '/' + source2)

        if os.path.isfile(destination + '/' + source3):
            os.remove(destination + '/' + source3)

        print("")
        print("Downloading...")
        urllib.request.urlretrieve("https://github.com/aboood40091/WiiUTools/raw/master/TexHaxU/gfd.dll", "gfd.dll")
        urllib.request.urlretrieve("https://github.com/aboood40091/WiiUTools/raw/master/TexHaxU/TexConv2.exe", "TexConv2.exe")
        urllib.request.urlretrieve("https://github.com/aboood40091/WiiUTools/raw/master/TexHaxU/texUtils.dll", "texUtils.dll")
        print("Download completed!")

        print("")
        print("Moving files...")
        
        if not os.path.isfile(destination + '/' + source1):
            shutil.move(source1, destination)

        if not os.path.isfile(destination + '/' + source2):
            shutil.move(source2, destination)

        if not os.path.isfile(destination + '/' + source3):
            shutil.move(source3, destination)

        with open("C:/Tex/new.txt", "w+") as txt:
            txt.write('v3.1')
            txt.close()
        
    top.title("BFLIM Tool v1.1")
    filemenu.add_command(label="Open File", command=openfile)
    filemenu.add_command(label="Open Folder", command=openfolder)
    menubar.add_cascade(label="File", menu=filemenu)

    top.config(menu=menubar)
    top.mainloop()

if __name__ == '__main__': main()
