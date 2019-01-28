# -*- mode: python -*-

block_cipher = None


a = Analysis(['test1.py'],
             pathex=['/home/john/Documents/Git/pdDesk'],
             binaries=[],
             datas=[('/home/john/Documents/Git/pdDesk/ui', '.'),
('/home/john/Documents/Git/pdDesk/ui/resources',  '.'),
('/home/john/Documents/Git/pdDesk/sample_data', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt4', 'matplotlib','scipy','wx','IPython'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='test1',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='test1')
