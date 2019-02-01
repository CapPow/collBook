# pyinstaller script for mac osx system
pyinstaller --clean --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --hidden-import='reportlab.graphics.barcode.code128' --hidden-import='reportlab.graphics.barcode.code93' --hidden-import='reportlab.graphics.barcode.usps' --hidden-import='reportlab.graphics.barcode.usps4s' --hidden-import='reportlab.graphics.barcode.ecc200datamatrix' -y collBook.py

# link (numpy/pandas): https://stackoverflow.com/questions/54316480/pyinstaller-with-pandas-and-numpy-exe-throws-error-at-runtime
# link (reportlab): https://stackoverflow.com/questions/38711221/installation-reportlab-importerror-no-module-named-reportlab-lib
