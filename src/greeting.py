"""A deterministic greeting with a small command-line interface."""
import argparse


def greet(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    if any(char in name for char in "\r\n\t\0"):
        raise ValueError("name must not contain CR, LF, TAB or NUL")
    cleaned = name.strip()
    if not 1 <= len(cleaned) <= 80:
        raise ValueError("name must contain 1 to 80 characters after trimming")
    return f"Hola, {cleaned}!"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Emit a validated greeting.")
    parser.add_argument("--name", required=True, help="Name to greet")
    args = parser.parse_args(argv)
    try:
        message = greet(args.name)
    except ValueError as error:
        parser.error(str(error))
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
