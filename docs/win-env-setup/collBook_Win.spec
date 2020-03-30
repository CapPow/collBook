# -*- mode: python -*-

block_cipher = None


a = Analysis(['collBook.py'],
             pathex=['C:\\Users\\qvd441\\Documents\\git\\collBook'],
             binaries=[],
             datas=[],
             hiddenimports=["reportlab.graphics.barcode.code39","reportlab.graphics.barcode.code93","reportlab.graphics.barcode.code128","reportlab.graphics.barcode.usps","reportlab.graphics.barcode.usps4s","reportlab.graphics.barcode.ecc200datamatrix","pkg_resources.py2_warn"],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4','matplotlib','scipy','wx','IPython','tkinter','tk'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
homepath='C:\\Users\\qvd441\\Documents\\git\\collBook\\venv\\Lib\\site-packages'
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='collBook',
          debug=False,
	  homepath=homepath,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, 
	  icon="collBookIcon.ico")
