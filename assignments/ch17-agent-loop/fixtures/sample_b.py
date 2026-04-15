import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.verbose:
        print("verbose mode")

if __name__ == "__main__":
    main()
