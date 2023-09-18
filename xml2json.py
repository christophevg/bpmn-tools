import logging
import xmltodict
import json
import sys

logger = logging.getLogger(__name__)

try:
  from AppKit import NSPasteboard, NSStringPboardType
  pb = NSPasteboard.generalPasteboard()
except ModuleNotFoundError:
  logger.debug("No AppKit installed, so no MacOS clipboard support!")
  pb = None

xml = None

# try paste board
if pb:
  xml = str(pb.stringForType_(NSStringPboardType))

# else try stdin
if not isinstance(xml, str) or xml.lstrip()[0] != "<":
  xml = sys.stdin.read()

print(json.dumps(xmltodict.parse(xml), indent=2))
