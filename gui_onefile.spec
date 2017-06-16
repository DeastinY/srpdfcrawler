# -*- mode: python -*-

block_cipher = None


a = Analysis(['gui.py'],
             pathex=['C:\\Users\\polzi\\Documents\\GitHub\\srpdfcrawler'],
             binaries=[],
             datas=[('pdftotext.exe', '.')],
             hiddenimports=["textract.parsers.pdf_parser"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='gui',
          debug=False,
          strip=False,
          upx=True,
          console=True )
