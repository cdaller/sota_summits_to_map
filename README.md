# SOTA Summits for OrganicMaps

Download kml files from [Sotl.as](https://sotl.as) for associations or regions and adds a color style, depening on the summit points.

The resulting kml file can then be imported as bookmarks into e.g. [OrganicMaps](https://organicmaps.app/).

The downloaded files are cached in the local file system.

## Usage

```bash
./sotlas_kml_with_styles.py OE/KT OE/ST DL HB
```

will download the regions "OE/KT" and "OE/ST" and the associations "DL" and "HB" from sotl.as, add style information to each summit and write it to local files (`OE_ST_styled.kml`, 'HB_styled.kml`, ...). These files can the be imported into various map applications.
