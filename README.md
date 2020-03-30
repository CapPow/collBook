# [Modernizing Field Collection Techniques](#readme)

<h1 align=center>
<img src="ui/resources/logo-collbook/horizontal.png" width=40%>
</h1>

collBook, is the desktop counterpart for the mobile app [collNotes](https://github.com/j-h-m/collNotes). Combined they are a field-to-database solution designed for field biologists to gather and format “born digital” field notes into database ready formats. A mobile application, collNote is being developed for Android and iOS devices to gather Darwin Core formatted field notes. A desktop application, collBook is being developed for Linux, OS X, and Windows to refine those field notes into portal ready Darwin Core files and specimen labels. Field note refinements include: reverse geocoding localities, taxonomic alignments, and creation of customizable labels which can optionally include catalog number barcodes.

## [Development stage](#Development-stage)

collBook is in a testing stage. **Please take caution with your data, and work on copies.** Pull requests, and comments are encouraged!

#### [Known bugs](#Known-bugs)
- Preview window zoom is not properly updated at start up. For now, altering the zoom after start up solves this.

## [Installation](#Installation)

 - Windows and Mac binaries are available under [releases](https://github.com/CapPow/collBook/releases). Be sure you unzip the folder before running the program. 
 - If you are interested in running, or building collBook from source you will need to place a Google geocoding API key in the following python file: "ui/apiKeys.py". To install the python dependencies, you can use "pip3 install -r requirements.txt" If you're interested in using pyinstaller, there are reference ".spec" files for Mac and Windows in the doc folder.

If you have any troubles, feel free to post in the [Issues section](https://github.com/CapPow/collBook/issues) or [contact us](https://github.com/CapPow/collBook#Contact-us).


## [Usage](#Usage)

collBook is designed to be used while formally identifying biological specimens, producing [symbiota](https://github.com/Symbiota/Symbiota) ready records and specimen labels. After opening collBook and customizing the preferences the steps to use collBook generally follow this order:
1. Load or transcribe field observations
    - Data collected in [collNotes](https://github.com/j-h-m/collNotes) can be loaded from the toolbar.
    - Field notes gathered in [iNaturalist](https://www.inaturalist.org/) or [ColectoR](http://camayal.info/colector.htm) may be loaded using the toolbar and an import dialog box to designate or generate site and specimen index fields.
    - Field notes gathered using traditional field journals may be directly transcribed into a new, empty, record list created using the toolbar.
2. Assign an identification for each record.
3. Refine the records using the toolbar button. The records to be refined are selected by the site navigation tree. Refinement steps are mostly automated and will occur in this order: 
    - Taxonomic verification, to verify name status and fill in blank or incorrect authorities.
    - Reverse geolocation, to populate location data from GPS coordinates and improve locality by prepending country, state, county, municipality and when relevant park name and nearest road or trail name.
    - Associated taxa assignment, to assemble a list of taxa identified from the same site.
    - Catalog number assignment and barcode generation, when opted for in preferences.
4. Review the label previews for record accuracy, and label preferences.
5. Export the records using the toolbar button, producing a symbiota ready CSV file and a PDF file containing labels to print. 

## [Contact us](#Contact-us)

For bug reports, feature requests, and suggestions you may post in the [Issues section](https://github.com/CapPow/collBook/issues), make pull requests, or contact us directly:

[Caleb Powell](https://github.com/CapPow) - BS Environmental Science, [Graduate Student - UTC](https://www.utc.edu/biology-geology-environmental-science/profiles/graduate-students/qvd441.php).

[Jacob Motley](https://www.linkedin.com/in/jacob-motley-b627a1152) - BS [Computer Science](https://github.com/j-h-m): Software Systems - UTC.

## [Citing collNotes & collBook](#Citation)

Please cite collNotes and collBook using our paper in *Applications in Plant Sciences*:

https://doi.org/10.1002/aps3.11284

Powell, C., Motley, J., Qin, H., and Shaw, J.. 2019. A born‐digital field‐to‐database solution for collections-based research using collNotes and collBook. *Applications in Plant Sciences* 7(8):e11284.

## [Credits](#Credits)

#### Catalog of Life
Roskov Y., Abucay L., Orrell T., Nicolson D., Bailly N., Kirk P.M., Bourgoin T., DeWalt R.E., Decock W., De Wever A., Nieukerken E. van, Zarucchi J., Penev L., eds. (2018). Species 2000 & ITIS Catalogue of Life, 2018 Annual Checklist. Digital resource at www.catalogueoflife.org/annual-checklist/2018. Species 2000: Naturalis, Leiden, the Netherlands. ISSN 2405-884X.

#### Feather Icons
Icons used in collBook are provided by [Feather Icons](https://github.com/feathericons/feather).

#### ITIS
the Integrated Taxonomic Information System (ITIS) (http://www.itis.gov).

#### Logo
[Project Logos](https://github.com/CapPow/collBook/tree/master/ui/resources/logo-collbook) for [collNotes](https://github.com/j-h-m/collNotes) and [collBook](https://github.com/CapPow/collBook) were designed by [Zularizal](https://github.com/zularizal). You can learn more about the design [here](https://steemit.com/utopian-io/@zularizal/logo-for-collbook-and-collnotes).

#### Mycobank
Vincent Robert, Duong Vu, Ammar Ben Hadj Amor, Nathalie van de Wiele, Carlo Brouwer, Bernard Jabas, Szaniszlo Szoke, Ahmed Dridi, Maher Triki, Samy ben Daoud, Oussema Chouchen, Lea Vaas, Arthur de Cock, Joost A. Stalpers, Dora Stalpers, Gerard J.M. Verkley, Marizeth Groenewald, Felipe Borges dos Santos, Gerrit Stegehuis, Wei Li, Linhuan Wu, Run Zhang, Juncai Ma, Miaomiao Zhou, Sergio Pérez Gorjón, Lily Eurwilaichitr, Supawadee Ingsriswang, Karen Hansen, Conrad Schoch, Barbara Robbertse, Laszlo Irinyi, Wieland Meyer, Gianluigi Cardinali, David L. Hawksworth, John W. Taylor, and Pedro W. Crous. 2013. MycoBank gearing up for new horizons. IMA Fungus · volume 4 · no 2: 371–379 

#### Taxonomic name resolution service (TNRS)
Boyle, B. et al. 2013. The taxonomic name resolution service: an online tool for automated standardization of plant names. BMC Bioinformatics 14:16. doi:10.1186/1471-2105-14-16
