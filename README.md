# Rock-Paper-Scissors with Commit-Reveal (Applied Cryptography – HW6)

Two-player Rock-Paper-Scissors played over a TCP socket between **Alice** (client) and **Bob** (server),
made fair with a **commit-reveal** protocol: each player first sends `SHA-256(move + salt)`,
then reveals move and salt, and the other side verifies the hash before the winner is decided.
Neither player can change their move after seeing the opponent's.

## Files
- `bob.py` – server (listens on port 5555)
- `alice.py` – client
- `report.pdf` – project report

## Run
```bash
python3 bob.py      # on machine/VM 1
python3 alice.py    # on machine/VM 2 (it asks for Bob's IP address at start)
```
Tested on two Ubuntu 24.04 VMs on a VirtualBox internal network.

## Possible improvements
- Generate the salt with `secrets.token_hex(16)` instead of `random.randint` (cryptographically secure, much larger space).
