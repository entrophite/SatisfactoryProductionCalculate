#!/usr/bin/env python3


def simplify_decimal(value: float, decimal: int = 3) -> str:
	fmt = ("{{:.{}f}}").format(decimal)
	plain = fmt.format(value)
	if "." not in plain:
		ret = plain
	else:
		ret = plain.rstrip("0").rstrip(".")
	return ret
