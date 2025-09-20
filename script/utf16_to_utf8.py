#!/usr/bin/env python3

import sys


def main():
	content = sys.stdin.buffer.read()
	utf8_content = content.decode("utf-16").encode("utf-8")
	sys.stdout.buffer.write(utf8_content)
	return


if __name__ == "__main__":
	main()
