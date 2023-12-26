import logging
import os
import sys

from fire import Fire

from bpmn_tools.tool import CLI

logger = logging.getLogger(__name__)

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
FORMAT    = "[%(asctime)s] [%(name)s] [%(process)d] [%(levelname)s] %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"
logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)

def cli():
  try:
    Fire(CLI(), name="bpmn-tool", command=sys.argv[1:] + ["--", "--separator=XXX"])
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  cli()
