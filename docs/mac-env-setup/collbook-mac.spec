# -*- mode: python ; coding: utf-8 -*-

# replace pathex and datas with your machine's path(s)

block_cipher = None


a = Analysis(['test1.py'],
             pathex=['/Users/jacob/Documents/Projects/pdDesk'],
             binaries=[],
             datas=[('/Users/jacob/Documents/Projects/pdDesk/key.txt','.')],
             hiddenimports=["reportlab.graphics.barcode.code39","reportlab.graphics.barcode.code93","reportlab.graphics.barcode.code128","reportlab.graphics.barcode.usps","reportlab.graphics.barcode.usps4s","reportlab.graphics.barcode.ecc200datamatrix"],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4','matplotlib','scipy','wx','IPython','tkinter','tk'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='collbook-mac',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )