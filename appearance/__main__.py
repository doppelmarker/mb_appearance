import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from appearance.app import main

if __name__ == "__main__":
    main()
