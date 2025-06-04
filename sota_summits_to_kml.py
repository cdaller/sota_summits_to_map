#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reads SOTA summit kml file from sotl.as, adds style info for placemarks depending on summit points.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import argparse
import urllib.request

# OrganicMaps does not load the icons from the urls, it just uses the style name to color the placemarks.
# But we provide some icons nevertheless, so that the KML can be used in other applications.
# OrganicMaps only supports fixed styles, so we use a fixed set of colors/styles.
STYLE_XML = '''<Style id="placemark-red">
    <IconStyle>
      <Icon>
        <href>https://raw.githubusercontent.com/cdaller/sota_summits_to_map/main/icons/placemark-red.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-deeporange">
    <IconStyle>
      <Icon>
        <href>https://raw.githubusercontent.com/cdaller/sota_summits_to_map/main/icons/placemark-orange.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-orange">
    <IconStyle>
      <Icon>
        <href>https://raw.githubusercontent.com/cdaller/sota_summits_to_map/main/icons/placemark-darkyellow.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-brown">
    <IconStyle>
      <Icon>
        <href>https://raw.githubusercontent.com/cdaller/sota_summits_to_map/main/icons/placemark-olive.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-lime">
    <IconStyle>
      <Icon>
        <href>https://raw.githubusercontent.com/cdaller/sota_summits_to_map/main/icons/placemark-lightgreen.png</href>
      </Icon>
    </IconStyle>
  </Style>
    <Style id="placemark-green">
    <IconStyle>
      <Icon>
        <href>https://raw.githubusercontent.com/cdaller/sota_summits_to_map/main/icons/placemark-darkgreen.png</href>
      </Icon>
    </IconStyle>
  </Style>
'''


def getStyle(points):
    if points == 10: 
        return 'red'
    if points >= 8: 
        return 'deeporange'
    if points >= 6: 
        return 'orange'
    if points >= 4: 
        return 'brown'
    if points >= 2:
        return 'lime'
    if points >= 1:
        return 'green'
    return 'green'

def process_kml_file(kml_content, outfilename):
    import xml.etree.ElementTree as ET
    import xml.etree.ElementTree as ET2
    ET.register_namespace('', "http://www.opengis.net/kml/2.2")
    ET.register_namespace('atom', "http://www.w3.org/2005/Atom")
    root = ET.fromstring(kml_content)
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    doc = root.find('kml:Document', ns)
    if doc is None:
        raise RuntimeError("<Document> element not found")
    styles = ET2.fromstring(f'<root>{STYLE_XML}</root>')
    for style in styles:
        doc.insert(0, style)
    for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        desc_elem = placemark.find('{http://www.opengis.net/kml/2.2}description')
        if desc_elem is not None and desc_elem.text:
            import re
            m = re.search(r'(\d+)pt', desc_elem.text)
            if m:
                points = int(m.group(1))
                style = getStyle(points)
                style_elem = placemark.find('{http://www.opengis.net/kml/2.2}styleUrl')
                if style_elem is not None:
                    placemark.remove(style_elem)
                from xml.etree.ElementTree import Element
                styleUrl = Element('{http://www.opengis.net/kml/2.2}styleUrl')
                styleUrl.text = f'#placemark-{style}'
                placemark.append(styleUrl)
    xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    Path(outfilename).write_bytes(xml_bytes)
    print(f"Wrote {outfilename}")

def assoc_to_filename(assoc):
    return assoc.replace('/', '_')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and style SOTA KML files by association/region code.")
    parser.add_argument('codes', nargs='+', help='SOTA association/region codes (e.g. OE OE/ST DL HB)')
    args = parser.parse_args()
    for code in args.codes:
        base_filename = code.replace('/', '_')
        src_filename = f"{base_filename}.kml"
        if Path(src_filename).exists():
            print(f"Using existing file {src_filename}")
            kml_content = Path(src_filename).read_bytes()
        else:
            if '/' in code:
                url = f"https://sotl.as/api/geoexport/regions/{code}.kml?nameopts=name"
            else:
                url = f"https://sotl.as/api/geoexport/associations/{code}.kml?nameopts=name"
            print(f"Downloading {url}")
            try:
                with urllib.request.urlopen(url) as resp:
                    kml_content = resp.read()
                Path(src_filename).write_bytes(kml_content)
                print(f"Saved {src_filename}")
            except Exception as e:
                print(f"Failed to download {url} ({e})")
                continue
        target_filename = f"{base_filename}_styled.kml"
        process_kml_file(kml_content, target_filename)
