#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BFLIM Tool
# Version 0.1
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
from tkinter.filedialog import askopenfilename
import tkinter.messagebox as messagebox
import urllib.request
import zipfile

top = Tk()
canvas = Canvas(top)
frame = Frame(canvas)
menubar = Menu(top)
filemenu = Menu(menubar, tearoff=0)

formats = {0x00000000: 'GX2_SURFACE_FORMAT_INVALID',
           0x00000001: 'GX2_SURFACE_FORMAT_TC_R8_UNORM',
           0x00000101: 'GX2_SURFACE_FORMAT_TC_R8_UINT',
           0x00000201: 'GX2_SURFACE_FORMAT_TC_R8_SNORM',
           0x00000301: 'GX2_SURFACE_FORMAT_TC_R8_SINT',
           0x00000002: 'GX2_SURFACE_FORMAT_T_R4_G4_UNORM',
           0x00000005: 'GX2_SURFACE_FORMAT_TCD_R16_UNORM',
           0x00000105: 'GX2_SURFACE_FORMAT_TC_R16_UINT',
           0x00000205: 'GX2_SURFACE_FORMAT_TC_R16_SNORM',
           0x00000305: 'GX2_SURFACE_FORMAT_TC_R16_SINT',
           0x00000806: 'GX2_SURFACE_FORMAT_TC_R16_FLOAT',
           0x00000007: 'GX2_SURFACE_FORMAT_TC_R8_G8_UNORM',
           0x00000107: 'GX2_SURFACE_FORMAT_TC_R8_G8_UINT',
           0x00000207: 'GX2_SURFACE_FORMAT_TC_R8_G8_SNORM',
           0x00000307: 'GX2_SURFACE_FORMAT_TC_R8_G8_SINT',
           0x00000008: 'GX2_SURFACE_FORMAT_TCS_R5_G6_B5_UNORM',
           0x0000000a: 'GX2_SURFACE_FORMAT_TC_R5_G5_B5_A1_UNORM',
           0x0000000b: 'GX2_SURFACE_FORMAT_TC_R4_G4_B4_A4_UNORM',
           0x0000000c: 'GX2_SURFACE_FORMAT_TC_A1_B5_G5_R5_UNORM',
           0x0000010d: 'GX2_SURFACE_FORMAT_TC_R32_UINT',
           0x0000030d: 'GX2_SURFACE_FORMAT_TC_R32_SINT',
           0x0000080e: 'GX2_SURFACE_FORMAT_TCD_R32_FLOAT',
           0x0000000f: 'GX2_SURFACE_FORMAT_TC_R16_G16_UNORM',
           0x0000010f: 'GX2_SURFACE_FORMAT_TC_R16_G16_UINT',
           0x0000020f: 'GX2_SURFACE_FORMAT_TC_R16_G16_SNORM',
           0x0000030f: 'GX2_SURFACE_FORMAT_TC_R16_G16_SINT',
           0x00000810: 'GX2_SURFACE_FORMAT_TC_R16_G16_FLOAT',
           0x00000011: 'GX2_SURFACE_FORMAT_D_D24_S8_UNORM',
           0x00000011: 'GX2_SURFACE_FORMAT_T_R24_UNORM_X8',
           0x00000111: 'GX2_SURFACE_FORMAT_T_X24_G8_UINT',
           0x00000811: 'GX2_SURFACE_FORMAT_D_D24_S8_FLOAT',
           0x00000816: 'GX2_SURFACE_FORMAT_TC_R11_G11_B10_FLOAT',
           0x00000019: 'GX2_SURFACE_FORMAT_TCS_R10_G10_B10_A2_UNORM',
           0x00000119: 'GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_UINT',
           0x00000219: 'GX2_SURFACE_FORMAT_T_R10_G10_B10_A2_SNORM',
           0x00000219: 'GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_SNORM',
           0x00000319: 'GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_SINT',
           0x0000001a: 'GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_UNORM',
           0x0000011a: 'GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_UINT',
           0x0000021a: 'GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_SNORM',
           0x0000031a: 'GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_SINT',
           0x0000041a: 'GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_SRGB',
           0x0000001b: 'GX2_SURFACE_FORMAT_TCS_A2_B10_G10_R10_UNORM',
           0x0000011b: 'GX2_SURFACE_FORMAT_TC_A2_B10_G10_R10_UINT',
           0x0000081c: 'GX2_SURFACE_FORMAT_D_D32_FLOAT_S8_UINT_X24',
           0x0000081c: 'GX2_SURFACE_FORMAT_T_R32_FLOAT_X8_X24',
           0x0000011c: 'GX2_SURFACE_FORMAT_T_X32_G8_UINT_X24',
           0x0000011d: 'GX2_SURFACE_FORMAT_TC_R32_G32_UINT',
           0x0000031d: 'GX2_SURFACE_FORMAT_TC_R32_G32_SINT',
           0x0000081e: 'GX2_SURFACE_FORMAT_TC_R32_G32_FLOAT',
           0x0000001f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_UNORM',
           0x0000011f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_UINT',
           0x0000021f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_SNORM',
           0x0000031f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_SINT',
           0x00000820: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_FLOAT',
           0x00000122: 'GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_UINT',
           0x00000322: 'GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_SINT',
           0x00000823: 'GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_FLOAT',
           0x00000031: 'GX2_SURFACE_FORMAT_T_BC1_UNORM',
           0x00000431: 'GX2_SURFACE_FORMAT_T_BC1_SRGB',
           0x00000032: 'GX2_SURFACE_FORMAT_T_BC2_UNORM',
           0x00000432: 'GX2_SURFACE_FORMAT_T_BC2_SRGB',
           0x00000033: 'GX2_SURFACE_FORMAT_T_BC3_UNORM',
           0x00000433: 'GX2_SURFACE_FORMAT_T_BC3_SRGB',
           0x00000034: 'GX2_SURFACE_FORMAT_T_BC4_UNORM',
           0x00000234: 'GX2_SURFACE_FORMAT_T_BC4_SNORM',
           0x00000035: 'GX2_SURFACE_FORMAT_T_BC5_UNORM',
           0x00000235: 'GX2_SURFACE_FORMAT_T_BC5_SNORM',
           0x00000081: 'GX2_SURFACE_FORMAT_T_NV12_UNORM'}

tileModes = {0x00: 'GX2_TILE_MODE_DEFAULT',
             0x01: 'GX2_TILE_MODE_LINEAR_ALIGNED',
             0x02: 'GX2_TILE_MODE_1D_TILED_THIN1',
             0x03: 'GX2_TILE_MODE_1D_TILED_THICK',
             0x04: 'GX2_TILE_MODE_2D_TILED_THIN1',
             0x05: 'GX2_TILE_MODE_2D_TILED_THIN2',
             0x06: 'GX2_TILE_MODE_2D_TILED_THIN4',
             0x07: 'GX2_TILE_MODE_2D_TILED_THICK',
             0x08: 'GX2_TILE_MODE_2B_TILED_THIN1',
             0x09: 'GX2_TILE_MODE_2B_TILED_THIN2',
             0x0a: 'GX2_TILE_MODE_2B_TILED_THIN4',
             0x0b: 'GX2_TILE_MODE_2B_TILED_THICK',
             0x0c: 'GX2_TILE_MODE_3D_TILED_THIN1',
             0x0d: 'GX2_TILE_MODE_3D_TILED_THICK',
             0x0e: 'GX2_TILE_MODE_3B_TILED_THIN1',
             0x0f: 'GX2_TILE_MODE_3B_TILED_THICK',
             0x10: 'GX2_TILE_MODE_LINEAR_SPECIAL'}

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

def surfaceGetBitsPerPixel(surfaceFormat):
    hwFormat = surfaceFormat & 0x3F
    bpp = formatHwInfo[hwFormat * 4 + 0]
    return bpp

class groups():
    pass

def find_name(f, name_pos):
    name = b""
    char = f[name_pos:name_pos + 1]
    i = 1

    while char != b"\x00":
        name += char
        
        char = f[name_pos + i:name_pos + i + 1]
        i += 1

    return(name.decode("utf-8"))

def DDStoBFLIM(flim, dds, f):
    with open(f, "rb") as inf:
        inb = inf.read()
        inf.close()

    name = os.path.splitext(dds)[0]

    os.system('C:\Tex\TexConv2.exe -i "' + dds + '" -o "' + name + '.gtx"')

    swizzle = (flim.swizzle & 0xFFF) >> 8
    format_ = flim.format
    tileMode = 4

    os.system('C:\Tex\TexConv2.exe -i "' + name + '.gtx" -f ' + formats[format_] + ' -tileMode ' + tileModes[tileMode] + ' -swizzle ' + str(swizzle) + ' -o "' + name + '2.gtx"')

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

            if info.format_ == 0x00000000:
                flim.format = 0x00000001
            elif info.format_ == 0x00000001:
                flim.format = 0x00000001
            elif info.format_ == 0x00000003:
                flim.format = 0x00000007
            elif info.format_ == 0x00000005:
                flim.format = 0x00000008
            elif info.format_ == 0x00000009:
                flim.format = 0x0000001a
            elif info.format_ == 0x00000014:
                flim.format = 0x0000001a
            elif info.format_ == 0x0000000C:
                flim.format = 0x00000031
            elif info.format_ == 0x00000012:
                flim.format = 0x00000031
            elif info.format_ == 0x00000015:
                flim.format = 0x00000031
            elif info.format_ == 0x0000000D:
                flim.format = 0x00000032
            elif info.format_ == 0x00000016:
                flim.format = 0x00000032
            elif info.format_ == 0x0000000E:
                flim.format = 0x00000033
            elif info.format_ == 0x00000017:
                flim.format = 0x00000033
            elif info.format_ == 0x0000000F:
                flim.format = 0x00000034
            elif info.format_ == 0x00000010:
                flim.format = 0x00000034
            elif info.format_ == 0x00000011:
                flim.format = 0x00000035
            elif info.format_ == 0x00000012:
                flim.format = 0x00000030

            flim.imageSize = info.imageSize

            flim.swizzle = info.swizzle
            flim.swizzle = (((flim.swizzle & 0xF0) >> 4) // 2) << 8
            assert info.swizzle == ((((flim.swizzle >> 8) * 2) << 4) & 0xF0) + 4

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
                os.system('C:\Tex\TexConv2.exe -i "' + name + '2.gtx" -f GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_UNORM -o "' + name + '.gtx"')
                os.system('C:\Tex\gtx_extract.exe "' + name + '.gtx"')
                os.remove(name + '.gtx')
                os.remove(name + '2.gtx')

            tv = 'Replace "' + os.path.basename(name) + '"'
            b = Button(frame, text=tv, command=lambda : DDStoBFLIM(flim, askopenfilename(parent=top, filetypes=options['filetypes']), filename))
            b.pack(padx=1, pady=1)
            
            menubar.destroy()
            filemenu.destroy()

            messagebox.showinfo("", "Done!")

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

def main():
    global tex
    global scr

    print("(C) 2017 AboodXD")

    if not os.path.isfile("C:\Tex\gtx_extract.exe"):
        print("")
        print("Downloading the necessary tools...")

        if not os.path.isdir("C:\Program Files (x86)"):
            print("")
            print("It seems like you have a 32-bit computer... Good luck getting this to work on it!")

        else:
            if not os.path.isdir("C:\Tex"):
                os.mkdir("C:\Tex")

            print("")
            print("Fetching GTX Extractor... ")
            print("")
            response = requests.get('https://github.com/aboood40091/GTX-Extractor/', verify=False)

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

            print("")
            print("Downloading...")
            urllib.request.urlretrieve("https://github.com/aboood40091/GTX-Extractor/releases/download/v4.0/gtx_extract_x64_v4.0.zip", "gtx_extract.zip")
            print("Download completed!")
            print("")
            print("Unzipping...")
            
            zip = zipfile.ZipFile(r'gtx_extract.zip')  
            zip.extractall(r'C:\Tex')
            
            print("File succesfully unzipped!")
            print("")
            print("Removing zipped file...")
            
            zip.close()
            os.remove("gtx_extract.zip")
            
            print("Zipped file succesfully removed!")

            if not os.path.isfile("C:\Tex\TexConv2.exe"):
                print("")
                print("Fetching TexConv2... ")
                print("")
                response = requests.get('https://github.com/NWPlayer123/WiiUTools/tree/master/TexHaxU', verify=False)

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

                print("")
                print("Downloading...")
                urllib.request.urlretrieve("https://github.com/NWPlayer123/WiiUTools/raw/master/TexHaxU/gfd.dll", "gfd.dll")
                urllib.request.urlretrieve("https://github.com/NWPlayer123/WiiUTools/raw/master/TexHaxU/TexConv2.exe", "TexConv2.exe")
                urllib.request.urlretrieve("https://github.com/NWPlayer123/WiiUTools/raw/master/TexHaxU/texUtils.dll", "texUtils.dll")
                print("Download completed!")

                print("")
                print("Moving files...")
                source1 = "gfd.dll"
                source2 = "TexConv2.exe"
                source3 = "texUtils.dll"
                destination = "C:\Tex"
                
                shutil.move(source1, destination)
                shutil.move(source2, destination)
                shutil.move(source3, destination)
        
    top.title("BFLIM Tool v0.1")
    filemenu.add_command(label="Open", command=openfile)
    menubar.add_cascade(label="File", menu=filemenu)

    top.config(menu=menubar)
    top.mainloop()

if __name__ == '__main__': main()
