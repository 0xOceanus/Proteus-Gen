#!/usr/bin/env python3
#
# | Author       : 0xOceanus
# | Name         : Proteus Gen
# | Contact      : github.com/0x0ceanus
#
#  This script is distributed for educational purposes only.
#
import sys
import uuid
import base64
import hashlib
import argparse
from Crypto.Cipher import AES
from Crypto.Cipher import ARC4
from colorama import Fore, Style
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

# ======================================================================
# Print Functions
# ======================================================================

def display_banner():
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
 ██▓███   ██▀███   ▒█████  ▄▄▄█████▓▓█████  █    ██   ██████ 
▓██░  ██▒▓██ ▒ ██▒▒██▒  ██▒▓  ██▒ ▓▒▓█   ▀  ██  ▓██▒▒██    ▒ 
▓██░ ██▓▒▓██ ░▄█ ▒▒██░  ██▒▒ ▓██░ ▒░▒███   ▓██  ▒██░░ ▓██▄   
▒██▄█▓▒ ▒▒██▀▀█▄  ▒██   ██░░ ▓██▓ ░ ▒▓█  ▄ ▓▓█  ░██░  ▒   ██▒
▒██▒ ░  ░░██▓ ▒██▒░ ████▓▒░  ▒██▒ ░ ░▒████▒▒▒█████▓ ▒██████▒▒
▒▓▒░ ░  ░░ ▒▓ ░▒▓░░ ▒░▒░▒░   ▒ ░░   ░░ ▒░ ░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
░▒ ░       ░▒ ░ ▒░  ░ ▒ ▒░     ░     ░ ░  ░░░▒░ ░ ░ ░ ░▒  ░ ░
░░         ░░   ░ ░ ░ ░ ▒    ░         ░    ░░░ ░ ░ ░  ░  ░  
            ░         ░ ░              ░  ░   ░           ░  
         Proteus: Simple Shellcode Obfuscator  {Style.RESET_ALL}
    """
    print(banner)

def msg_info(msg):
    print(f"{Fore.BLUE}{Style.BRIGHT}[*]{Style.RESET_ALL} {msg}")

def msg_warning(msg):
    print(f"{Fore.YELLOW}{Style.BRIGHT}[!]{Style.RESET_ALL} {msg}")

def msg_error(msg):
    print(f"{Fore.RED}{Style.BRIGHT}[X]{Style.RESET_ALL} {msg}")

def msg_success(msg):
    print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} {msg}")

# ======================================================================
# Encryption Functions
# ======================================================================

def xor_encrypt(data, key):
    """Single-byte XOR — used for randomly generated keys."""
    return bytes(byte ^ key for byte in data)

def xor_encrypt_multibyte(data, key):
    """
    Repeating/cycling XOR — used when a plain-text passphrase is provided.

    Each byte of data is XOR'd against key[i % len(key)], so the key
    repeats across the entire payload rather than being a single byte.
    With a passphrase like 'SecretKey' (9 bytes):
      data[0] ^ 'S', data[1] ^ 'e', ..., data[8] ^ 'y',
      data[9] ^ 'S', data[10] ^ 'e', ...
    """
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))

def aes_encrypt(data, key):
    """AES-256 CBC mode. Prepends the IV to the ciphertext."""
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    return iv + ciphertext

def rc4_encrypt(data, key):
    """RC4 stream cipher encryption."""
    cipher = ARC4.new(key)
    return cipher.encrypt(data)

# ======================================================================
# Formatting Functions
# ======================================================================

def format_as_c(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a C unsigned char array.

    Example output:
      unsigned char buf[] = {
        0xfc, 0xe8, 0x82
      };
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    lines = []
    for i in range(0, len(hex_bytes), bytes_per_line):
        chunk = ", ".join(hex_bytes[i:i + bytes_per_line])
        lines.append(f"  {chunk}")
    output = f"unsigned char {var_name}[] = {{\n"
    output += ",\n".join(lines)
    output += "\n};"
    return output

def format_as_csharp(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a C# byte array.

    Example output:
      byte[] buf = new byte[3] {
      0xfc,0xe8,0x82};
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    lines = []
    for i in range(0, len(hex_bytes), bytes_per_line):
        chunk = ",".join(hex_bytes[i:i + bytes_per_line])
        lines.append(chunk)
    output = f"byte[] {var_name} = new byte[{len(data)}] {{"
    output += "\n" + ",\n".join(lines)
    output += "};"
    return output

def format_as_golang(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a Go byte slice.

    Example output:
      buf := []byte{
          0xfc,0xe8,0x82,
      }
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    lines = []
    for i in range(0, len(hex_bytes), bytes_per_line):
        chunk = ",".join(hex_bytes[i:i + bytes_per_line])
        lines.append(chunk)
    output = f"{var_name} := []byte{{\n"
    output += ",\n".join(lines)
    output += "};"
    return output

def format_as_powershell(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a PowerShell byte array.

    Example output:
      [Byte[]] $buf = 0xfc,0xe8,0x82,...
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    chunks = [
        ",".join(hex_bytes[i:i + bytes_per_line])
        for i in range(0, len(hex_bytes), bytes_per_line)
    ]
    return f"[Byte[]] ${var_name} = " + ",\n".join(chunks)

def format_as_python(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a Python byte string literal.

    Example output:
      buf = b'\\xfc\\xe8\\x82...'
    """
    hex_bytes = [f"\\x{b:02x}" for b in data]
    chunks = [
        "".join(hex_bytes[i:i + bytes_per_line])
        for i in range(0, len(hex_bytes), bytes_per_line)
    ]
    return f'{var_name} = b"' + '"\\\n        b"'.join(chunks) + '"'

def format_as_rust(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a Rust byte array.

    Example output:
      let buf: [u8; N] = [
          0xfc, 0xe8, 0x82, ...
      ];
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    chunks = [
        ", ".join(hex_bytes[i:i + bytes_per_line])
        for i in range(0, len(hex_bytes), bytes_per_line)
    ]
    inner = ",\n    ".join(chunks)
    return f"let {var_name}: [u8; {len(data)}] = [\n    {inner}\n];"


def format_as_php(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a PHP binary string.

    Example output:
      $buf = "\\xfc\\xe8\\x82...";
    """
    hex_bytes = [f"\\x{b:02x}" for b in data]
    chunks = [
        "".join(hex_bytes[i:i + bytes_per_line])
        for i in range(0, len(hex_bytes), bytes_per_line)
    ]
    return f'${var_name} = "' + '".\n        ."'.join(chunks) + '";'

def format_as_js(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a JavaScript Uint8Array.

    Example output:
      var buf = new Uint8Array([
        0xfc, 0xe8, 0x82, ...
      ]);
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    lines = []
    for i in range(0, len(hex_bytes), bytes_per_line):
        chunk = ", ".join(hex_bytes[i:i + bytes_per_line])
        lines.append(f"  {chunk}")
    return f"var {var_name} = new Uint8Array([\n" + ",\n".join(lines) + "\n]);"

def format_as_nim(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a Nim byte array.

    Example output:
      var buf: array[N, byte] = [
        byte 0xfc, 0xe8, 0x82, ...
      ]
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    lines = []
    for i in range(0, len(hex_bytes), bytes_per_line):
        chunk = ", ".join(hex_bytes[i:i + bytes_per_line])
        # Only the first element needs the 'byte' type prefix.
        prefix = "byte " if i == 0 else "     "
        lines.append(f"  {prefix}{chunk}")
    return f"var {var_name}: array[{len(data)}, byte] = [\n" + ",\n".join(lines) + "\n]"

def format_as_zig(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a Zig byte array.

    Example output:
      const buf = [_]u8{
          0xfc, 0xe8, 0x82, ...
      };
    """
    hex_bytes = [f"0x{b:02x}" for b in data]
    lines = []
    for i in range(0, len(hex_bytes), bytes_per_line):
        chunk = ", ".join(hex_bytes[i:i + bytes_per_line])
        lines.append(f"    {chunk}")
    return f"const {var_name} = [_]u8{{\n" + ",\n".join(lines) + "\n};"

def format_as_ruby(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a Ruby binary string.

    Example output:
      buf = "\\xfc\\xe8\\x82..."
    """
    hex_bytes = [f"\\x{b:02x}" for b in data]
    chunks = [
        "".join(hex_bytes[i:i + bytes_per_line])
        for i in range(0, len(hex_bytes), bytes_per_line)
    ]
    return f'{var_name} = "' + '"\\\n       "'.join(chunks) + '"'

def format_as_java(data, var_name="buf", bytes_per_line=16):
    """
    Converts to a Java byte array.

    Java's byte is signed (-128 to 127), so values above 0x7f must be
    cast with (byte) to avoid a compile-time narrowing error.

    Example output:
      byte[] buf = new byte[] {
          (byte)0xfc, (byte)0xe8, (byte)0x82, ...
      };
    """
    hex_bytes = [f"(byte)0x{b:02x}" for b in data]
    lines = []
    for i in range(0, len(hex_bytes), bytes_per_line):
        chunk = ", ".join(hex_bytes[i:i + bytes_per_line])
        lines.append(f"    {chunk}")
    return f"byte[] {var_name} = new byte[] {{\n" + ",\n".join(lines) + "\n};"

def format_as_b64(data):
    return base64.b64encode(data).decode()

def format_as_hex(data):
    return data.hex()

def format_key(key, output_format):
    # XOR keys are stored as a plain int; normalise to bytes first.
    if isinstance(key, int):
        key = bytes([key])

    if output_format == "c":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"unsigned char key[] = {{{hex_bytes}}};"

    elif output_format == "csharp":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"byte[] key = {{{hex_bytes}}};"

    elif output_format == "golang":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"key := []byte{{{hex_bytes}}}"

    elif output_format == "powershell":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"[Byte[]] $key = {hex_bytes}"

    elif output_format == "python":
        hex_bytes = ''.join(f'\\x{b:02x}' for b in key)
        return f'key = b"{hex_bytes}"'

    elif output_format == "rust":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"let key: [u8; {len(key)}] = [{hex_bytes}];"


    elif output_format == "php":
        hex_bytes = ''.join(f'\\x{b:02x}' for b in key)
        return f'$key = "{hex_bytes}";'

    elif output_format == "js":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"var key = new Uint8Array([{hex_bytes}]);"

    elif output_format == "nim":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"var key = [byte {hex_bytes}]"

    elif output_format == "zig":
        hex_bytes = ', '.join(f'0x{b:02x}' for b in key)
        return f"const key = [_]u8{{{hex_bytes}}};"

    elif output_format == "ruby":
        hex_bytes = ''.join(f'\\x{b:02x}' for b in key)
        return f'key = "{hex_bytes}"'

    elif output_format == "java":
        hex_bytes = ', '.join(f'(byte)0x{b:02x}' for b in key)
        return f"byte[] key = new byte[] {{{hex_bytes}}};"

    elif output_format == "base64":
        return format_as_b64(key)

    elif output_format == "hex":
        return key.hex()

    elif output_format == "raw":
        return key

    # Should never reach here given argparse choices validation.
    msg_error(f"Unknown output format: {output_format}")
    sys.exit(1)

# ======================================================================
# Utility Functions
# ======================================================================

def write_file(filename, data):
    if isinstance(data, bytes):
        with open(filename, "wb") as f:
            f.write(data)
    elif isinstance(data, str):
        with open(filename, "w") as f:
            f.write(data)

def get_file_size(bytes_size):
    units = ['B', 'KB', 'MB', 'GB']
    for unit in units:
        if bytes_size < 1024 or unit == units[-1]:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024

def default_filenames():
    short_hex = uuid.uuid4().hex[:16]
    return {
        'key':       f"key_{short_hex}.key",
        'shellcode': f"shellcode_{short_hex}.bin",
    }

def load_shellcode(input_path):
    try:
        if input_path == '-':
            shellcode = sys.stdin.buffer.read()
            msg_info("Input file: <stdin>")
        else:
            with open(input_path, "rb") as f:
                shellcode = f.read()
            msg_info(f"Input file: {input_path}")
        if not shellcode:
            msg_error("Input is empty — nothing to process.")
            sys.exit(1)
        msg_info(f"File size:  {len(shellcode)} bytes ({get_file_size(len(shellcode))})")
        return shellcode
    except IOError as e:
        msg_error(str(e))
        sys.exit(1)

# Expected key length (bytes) for each supported algorithm.
KEY_SIZES = {
    'xor': 1,
    'rc4': 32,
    'aes': 32,
}

def parse_user_key(hex_key, algorithm):
    """
    Validate and decode a hex-encoded key supplied via --key.

    Always expects a valid hex string of the correct length:
      XOR : 2 hex chars  (1 byte)
      RC4 : 64 hex chars (32 bytes)
      AES : 64 hex chars (32 bytes)

    For plain-text passphrases use -p/--passphrase instead.

    Returns an int for XOR, bytes for RC4/AES.
    """
    try:
        key_bytes = bytes.fromhex(hex_key)
    except ValueError:
        msg_error(
            "--key must be a valid hex string (e.g. deadbeef...). "
            "For a plain-text passphrase use -p/--passphrase."
        )
        sys.exit(1)

    expected = KEY_SIZES[algorithm]
    if len(key_bytes) != expected:
        msg_error(
            f"{algorithm.upper()} requires a {expected}-byte key "
            f"({expected * 2} hex characters). "
            f"Received {len(key_bytes)} byte(s)."
        )
        sys.exit(1)

    # XOR encrypt() expects a plain int, not bytes.
    return key_bytes[0] if algorithm == 'xor' else key_bytes

def derive_key_from_passphrase(passphrase, algorithm):
    # XOR: use the passphrase as the cycling key
    if algorithm == 'xor':
        return passphrase.encode('utf-8')

    # RC4 / AES: SHA-256 the passphrase to produce exactly 32 bytes.
    return hashlib.sha256(passphrase.encode('utf-8')).digest()

def process_encryption(shellcode, args):
    """
    Optionally encrypt the shellcode.

    If --key is provided the user-supplied key is used;
    otherwise a fresh random key is generated.
    Returns (processed_data, enc_key) where enc_key is None
    when no encryption was requested.
    """
    if not args.enc:
        msg_warning("No encryption specified.")
        return shellcode, None

    msg_info(f"Specified Encryption:  {args.enc.upper()}")

    # Unpack the default random-key generator for this algorithm.
    encrypt_func, enc_key = ENCRYPTION_FUNCS[args.enc]()

    if args.passphrase:
        enc_key = derive_key_from_passphrase(args.passphrase, args.enc)
        if args.enc == 'xor':
            # Upgrade to multi-byte cycling XOR for passphrase keys.
            # Random keys keep the original single-byte xor_encrypt.
            encrypt_func = xor_encrypt_multibyte
            msg_info(f"Key source:  passphrase (multi-byte XOR, {len(enc_key)}-byte cycle)")
        else:
            msg_info("Key source:  passphrase (SHA-256 derived)")
    elif args.key:
        enc_key = parse_user_key(args.key, args.enc)
        msg_info("Key source:  user-supplied hex")
    else:
        msg_info("Key source:  randomly generated")

    print()
    processed_data = encrypt_func(shellcode, enc_key)
    return processed_data, enc_key

def handle_key_output(enc_key, format_type, key_filename):
    """Format the key and write it to a file."""
    key_display = format_key(enc_key, format_type)
    write_file(key_filename, key_display)
    msg_success(f"Key written to:       {key_filename}")

def handle_shellcode_output(output_data, args, files):
    """Write the formatted shellcode to a file or print it to stdout."""
    if args.output:
        output_path = args.output
    elif args.format == "raw" and files:
        output_path = files['shellcode']
    else:
        output_path = None

    if output_path:
        write_file(output_path, output_data)
        msg_success(f"Shellcode written to: {output_path}")
    else:
        msg_success("Final payload:")
        print(output_data)

# ======================================================================
# Encryption and format dispatch tables
# ======================================================================

ENCRYPTION_FUNCS = {
    'xor': lambda: (xor_encrypt, get_random_bytes(1)[0]),
    'rc4': lambda: (rc4_encrypt, get_random_bytes(32)),
    'aes': lambda: (aes_encrypt, get_random_bytes(32)),
}

FORMAT_FUNCS = {
    'c':          format_as_c,
    'csharp':     format_as_csharp,
    'golang':     format_as_golang,
    'powershell': format_as_powershell,
    'python':     format_as_python,
    'rust':       format_as_rust,
    'php':        format_as_php,
    'js':         format_as_js,
    'nim':        format_as_nim,
    'zig':        format_as_zig,
    'ruby':       format_as_ruby,
    'java':       format_as_java,
    'base64':     format_as_b64,
    'hex':        format_as_hex,
    'raw':        lambda x: x,
}

# ======================================================================
# Main
# ======================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Proteus Gen — Simple Shellcode Obfuscator"
    )

    io_group = parser.add_argument_group('input/output')
    io_group.add_argument(
        "-i", "--input", required=True, metavar='',
        help="path to the raw shellcode file."
    )
    io_group.add_argument(
        "-o", "--output", metavar='',
        help="path to write the output file."
    )

    proc_group = parser.add_argument_group('processing')
    proc_group.add_argument(
        "-e", "--enc", metavar='',
        help="encryption algorithm to apply.",
        choices=['xor', 'rc4', 'aes']
    )
    proc_group.add_argument(
        "-f", "--format", required=True, metavar='',
        help="output format for the shellcode.",
        choices=['base64', 'c', 'csharp', 'golang', 'hex',
                 'java', 'js', 'nim', 'php', 'powershell',
                 'python', 'raw', 'ruby', 'rust', 'zig']
    )
    # --key and --passphrase are mutually exclusive; only one may be given.
    key_group = proc_group.add_mutually_exclusive_group()
    key_group.add_argument(
        "-k", "--key", metavar='',
        help=(
            "hex-encoded encryption key (requires -e). "
            "XOR: 2 hex chars (1 byte); RC4/AES: 64 hex chars (32 bytes)."
        )
    )
    key_group.add_argument(
        "-p", "--passphrase", metavar='',
        help=(
            "plain-text passphrase to derive an encryption key from (requires -e). "
            "The passphrase is hashed with SHA-256 to produce the key bytes."
        )
    )

    args = parser.parse_args()

    display_banner()

    # Both key flags require an encryption algorithm to be selected.
    if (args.key or args.passphrase) and not args.enc:
        flag = "--key" if args.key else "--passphrase"
        msg_error(f"{flag} requires --enc to be specified.")
        sys.exit(1)

    # Generate unique filenames upfront when raw output is selected,
    # since both the key and the shellcode will be written to disk.
    files = default_filenames() if args.format == "raw" else None

    # Load
    shellcode = load_shellcode(args.input)
    msg_info(f"Specified Format: {args.format}")
    
    # Encrypt
    processed_data, enc_key = process_encryption(shellcode, args)

    # Output the key
    if enc_key is not None:
        if args.format == "raw":
            handle_key_output(enc_key, args.format, files['key'])
        else:
            key_display = format_key(enc_key, args.format)
            msg_success(f"Key ({args.format}):\n{key_display}")

    # Format and output the shellcode
    output_data = FORMAT_FUNCS[args.format](processed_data)
    print()
    handle_shellcode_output(output_data, args, files)


if __name__ == '__main__':
    main()
