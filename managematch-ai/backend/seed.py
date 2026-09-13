import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.scripts.seed import main, seed_database

if __name__ == "__main__":
    main()
