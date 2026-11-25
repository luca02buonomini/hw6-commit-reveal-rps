

import socket
import hashlib
import random
import json
import sys


MOSSE_VALIDE = ["rock", "paper", "scissors"]
PORTA = 5555



def genera_salt():
    """
    Genera un numero casuale (salt) per rendere unico l'hash.
    """
    return str(random.randint(100000, 999999))

def crea_commit(mossa, salt):
    """
    Crea un hash crittografico della mossa + salt.
    """
    messaggio = mossa + salt
    return hashlib.sha256(messaggio.encode()).hexdigest()

def verifica_commit(mossa, salt, commit_ricevuto):
    """
    Verifica che la mossa rivelata corrisponda al commit iniziale.
    """
    commit_calcolato = crea_commit(mossa, salt)
    return commit_calcolato == commit_ricevuto



def determina_vincitore(mossa1, mossa2):
    """
    Determina chi vince (giocatore1 = Bob, giocatore2 = Alice).
    """
    if mossa1 == mossa2:
        return "pareggio"
    
    vittorie = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }
    
    if vittorie[mossa1] == mossa2:
        return "giocatore1"
    else:
        return "giocatore2"



class Alice:
    def __init__(self, host, porta=PORTA):
        self.host = host
        self.porta = porta
        self.socket = None
        
    def connetti(self):
        """
        Crea un socket TCP e si connette a Bob.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[ALICE] 🚀 Connessione a Bob ({self.host}:{self.porta})...")
        sys.stdout.flush()
        self.socket.connect((self.host, self.porta))
        print("[ALICE] ✓ Connessa a Bob!\n")
        sys.stdout.flush()
        
    def invia_messaggio(self, messaggio):
        """
        Invia un messaggio JSON a Bob.
        """
        dati = json.dumps(messaggio).encode()
        self.socket.sendall(dati + b"\n")
        
    def ricevi_messaggio(self):
        """
        Riceve un messaggio JSON da Bob.
        """
        dati = b""
        while b"\n" not in dati:
            dati += self.socket.recv(1024)
        return json.loads(dati.decode().strip())
    
    def gioca(self):
        """
        Esegue il protocollo di gioco completo.
        """
        print("=" * 50)
        print("          INIZIA LA PARTITA")
        print("=" * 50)
        sys.stdout.flush()
        
        
        print("\n[ALICE] Scegli la tua mossa:")
        for i, mossa in enumerate(MOSSE_VALIDE, 1):
            print(f"  {i}. {mossa}")
        sys.stdout.flush()
        
        while True:
            try:
                scelta = int(input("\nInserisci il numero (1-3): ")) - 1
                if 0 <= scelta < len(MOSSE_VALIDE):
                    break
                else:
                    print("Numero non valido! Scegli 1, 2 o 3.")
                    sys.stdout.flush()
            except ValueError:
                print("Inserisci un numero valido!")
                sys.stdout.flush()
        
        mia_mossa = MOSSE_VALIDE[scelta]
        
        
        mio_salt = genera_salt()
        mio_commit = crea_commit(mia_mossa, mio_salt)
        print(f"\n[ALICE] ✓ Mossa scelta: {mia_mossa}")
        print(f"[ALICE] ✓ Salt generato: {mio_salt}")
        print(f"[ALICE] ✓ Commit creato: {mio_commit[:16]}...")
        sys.stdout.flush()
        
        
        print("\n" + "=" * 50)
        print("          FASE 1: COMMIT")
        print("=" * 50)
        sys.stdout.flush()
        
        print("[ALICE] Attendo il commit di Bob...")
        sys.stdout.flush()
        msg_bob = self.ricevi_messaggio()
        commit_bob = msg_bob["commit"]
        print(f"[ALICE] ✓ Commit di Bob ricevuto: {commit_bob[:16]}...")
        sys.stdout.flush()
        
        print("[ALICE] Invio del mio commit a Bob...")
        sys.stdout.flush()
        self.invia_messaggio({"tipo": "commit", "commit": mio_commit})
        
        
        print("\n" + "=" * 50)
        print("          FASE 2: REVEAL")
        print("=" * 50)
        sys.stdout.flush()
        
        print("[ALICE] Attendo la reveal di Bob...")
        sys.stdout.flush()
        reveal_bob = self.ricevi_messaggio()
        mossa_bob = reveal_bob["mossa"]
        salt_bob = reveal_bob["salt"]
        print(f"[ALICE] ✓ Mossa di Bob ricevuta: {mossa_bob}")
        sys.stdout.flush()
        
        print("[ALICE] Invio della mia mossa e salt a Bob...")
        sys.stdout.flush()
        self.invia_messaggio({
            "tipo": "reveal",
            "mossa": mia_mossa,
            "salt": mio_salt
        })
        
        
        print("\n" + "=" * 50)
        print("          FASE 3: VERIFICA")
        print("=" * 50)
        sys.stdout.flush()
        
        print("[ALICE] Verifico che Bob non abbia barato...")
        sys.stdout.flush()
        if not verifica_commit(mossa_bob, salt_bob, commit_bob):
            print("[ALICE] ⚠️  ATTENZIONE: Bob ha barato! Il commit non corrisponde!")
            sys.stdout.flush()
            return
        
        print("[ALICE] ✓ Verifica superata: Bob ha giocato onestamente")
        sys.stdout.flush()
        
        
        print("\n" + "=" * 50)
        print("          RISULTATO FINALE")
        print("=" * 50)
        sys.stdout.flush()
        
        print(f"\n[ALICE] La mia mossa: {mia_mossa.upper()}")
        print(f"[ALICE] Mossa di Bob: {mossa_bob.upper()}")
        sys.stdout.flush()
        
        vincitore = determina_vincitore(mossa_bob, mia_mossa)
        print()
        if vincitore == "pareggio":
            print("[ALICE] 🤝 PAREGGIO!")
        elif vincitore == "giocatore1":
            print("[ALICE] 😞 HA VINTO BOB!")
        else:
            print("[ALICE] 🎉 HO VINTO!")
        
        print("\n" + "=" * 50)
        sys.stdout.flush()
    
    def chiudi(self):
        """
        Chiude la connessione.
        """
        if self.socket:
            self.socket.close()
        print("\n[ALICE] Connessione chiusa. Arrivederci!")
        sys.stdout.flush()



if __name__ == "__main__":
    print("=" * 50)
    print("   PROTOCOLLO ROSHAMBO SICURO - ALICE (CLIENT)")
    print("=" * 50)
    print()
    sys.stdout.flush()
    
    
    print("Inserisci l'indirizzo IP di Bob:")
    print("  - Per test locale: 'localhost' o '127.0.0.1'")
    print("  - Per VirtualBox: l'IP della VM di Bob (es: 192.168.x.x)")
    print("  - Premi INVIO per usare 'localhost'")
    sys.stdout.flush()
    
    try:
        host = input("\nIndirizzo IP: ").strip()
    except EOFError:
        print("\n[ALICE] ERRORE: Impossibile leggere input. Usa un terminale separato!")
        sys.stdout.flush()
        input("\nPremi INVIO per uscire...")
        sys.exit(1)
    
    if not host:
        host = "localhost"
        print(f"[ALICE] Uso indirizzo default: {host}")
        sys.stdout.flush()
    
    print()
    sys.stdout.flush()
    
    alice = Alice(host)
    try:
        alice.connetti()
        alice.gioca()
    except KeyboardInterrupt:
        print("\n\n[ALICE] Interruzione da tastiera...")
        sys.stdout.flush()
    except ConnectionRefusedError:
        print(f"\n[ALICE] ❌ Errore: Impossibile connettersi a Bob su {host}:{PORTA}")
        print("[ALICE] Assicurati che Bob sia in esecuzione!")
        sys.stdout.flush()
    except Exception as e:
        print(f"\n[ALICE] Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
    finally:
        alice.chiudi()
        input("\nPremi INVIO per chiudere...")
