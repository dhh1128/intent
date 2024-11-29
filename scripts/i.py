if __name__ == "__main__":
    import os
    import sys

    # Try loading an installed python package. If not installed, then
    # we're in dev mode. Try loading from path relative to this script
    # instead.
    try:
        from intent.app import main
    except ModuleNotFoundError:
        MY_FOLDER = os.path.dirname(os.path.realpath(os.path.abspath(os.path.normpath(__file__))))
        sys.path.insert(0, os.path.abspath(os.path.join(MY_FOLDER, '..')))
        from intent.app import main

    main()
