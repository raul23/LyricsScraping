import argparse
import os
import sqlite3
import time


if __name__ == '__main__':
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Create SQLite database")
    parser.add_argument("-o", action="store_true", dest="overwrite",
                        default=False,
                        help="Overwrite the database file")
    parser.add_argument("-d", "--database", default="database.sqlite",
                        help="Path to the SQLite database file")
    parser.add_argument("-s", "--schema", required=True,
                        help="Path to the schema file")
    # Process command-line arguments
    args = parser.parse_args()

    db_exists = os.path.exists(args.database)

    if args.overwrite and db_exists:
        print("WARNING: {} will be overwritten ...".format(args.database))
        # Exit program before delay expires or the database is overwritten
        time.sleep(5)
        os.remove(args.database)

    if not db_exists or args.overwrite:
        print("Creating database")
        with sqlite3.connect(args.database) as conn:
            try:
                with open(args.schema, 'rt') as f:
                    schema = f.read()
                    conn.executescript(schema)
            except IOError as e:
                raise IOError(e)
            else:
                print("Database created!")
    else:
        print("Database '{}' already exists!".format(args.database))
