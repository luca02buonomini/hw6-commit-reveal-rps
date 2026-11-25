

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


class Bob:
    def __init__(self, porta=PORTA):
        self.porta = porta
        self.socket = None
        self.connessione = None
        
    def avvia_server(self):
        """
        Crea un socket TCP e si mette in ascolto.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("0.0.0.0", self.porta))
        self.socket.listen(1)
        print(f"[BOB] 🚀 Server in ascolto sulla porta {self.porta}...")
        print(f"[BOB] In attesa che Alice si connetta...")
        sys.stdout.flush()
        
    def accetta_connessione(self):
        """
        Accetta la connessione da Alice.
        """
        self.connessione, indirizzo = self.socket.accept()
        print(f"[BOB] ✓ Alice connessa da {indirizzo}\n")
        sys.stdout.flush()
        
    def invia_messaggio(self, messaggio):
        """
        Invia un messaggio JSON ad Alice.
        """
        dati = json.dumps(messaggio).encode()
        self.connessione.sendall(dati + b"\n")
        
    def ricevi_messaggio(self):
        """
        Riceve un messaggio JSON da Alice.
        """
        dati = b""
        while b"\n" not in dati:
            dati += self.connessione.recv(1024)
        return json.loads(dati.decode().strip())
    
    def gioca(self):
        """
        Esegue il protocollo di gioco completo.
        """
        print("=" * 50)
        print("          INIZIA LA PARTITA")
        print("=" * 50)
        sys.stdout.flush()
        
        
        print("\n[BOB] Scegli la tua mossa:")
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
        print(f"\n[BOB] ✓ Mossa scelta: {mia_mossa}")
        print(f"[BOB] ✓ Salt generato: {mio_salt}")
        print(f"[BOB] ✓ Commit creato: {mio_commit[:16]}...")
        sys.stdout.flush()
        
        
        print("\n" + "=" * 50)
        print("          FASE 1: COMMIT")
        print("=" * 50)
        sys.stdout.flush()
        
        print("[BOB] Invio del mio commit ad Alice...")
        sys.stdout.flush()
        self.invia_messaggio({"tipo": "commit", "commit": mio_commit})
        
        print("[BOB] Attendo il commit di Alice...")
        sys.stdout.flush()
        msg_alice = self.ricevi_messaggio()
        commit_alice = msg_alice["commit"]
        print(f"[BOB] ✓ Commit di Alice ricevuto: {commit_alice[:16]}...")
        sys.stdout.flush()
        
        
        print("\n" + "=" * 50)
        print("          FASE 2: REVEAL")
        print("=" * 50)
        sys.stdout.flush()
        
        print("[BOB] Invio della mia mossa e salt ad Alice...")
        sys.stdout.flush()
        self.invia_messaggio({
            "tipo": "reveal",
            "mossa": mia_mossa,
            "salt": mio_salt
        })
        
        print("[BOB] Attendo la reveal di Alice...")
        sys.stdout.flush()
        reveal_alice = self.ricevi_messaggio()
        mossa_alice = reveal_alice["mossa"]
        salt_alice = reveal_alice["salt"]
        print(f"[BOB] ✓ Mossa di Alice ricevuta: {mossa_alice}")
        sys.stdout.flush()
        
        
        print("\n" + "=" * 50)
        print("          FASE 3: VERIFICA")
        print("=" * 50)
        sys.stdout.flush()
        
        print("[BOB] Verifico che Alice non abbia barato...")
        sys.stdout.flush()
        if not verifica_commit(mossa_alice, salt_alice, commit_alice):
            print("[BOB] ⚠️  ATTENZIONE: Alice ha barato! Il commit non corrisponde!")
            sys.stdout.flush()
            return
        
        print("[BOB] ✓ Verifica superata: Alice ha giocato onestamente")
        sys.stdout.flush()
        
        
        print("\n" + "=" * 50)
        print("          RISULTATO FINALE")
        print("=" * 50)
        sys.stdout.flush()
        
        print(f"\n[BOB] La mia mossa: {mia_mossa.upper()}")
        print(f"[BOB] Mossa di Alice: {mossa_alice.upper()}")
        sys.stdout.flush()
        
        vincitore = determina_vincitore(mia_mossa, mossa_alice)
        print()
        if vincitore == "pareggio":
            print("[BOB] 🤝 PAREGGIO!")
        elif vincitore == "giocatore1":
            print("[BOB] 🎉 HO VINTO!")
        else:
            print("[BOB] 😞 HA VINTO ALICE!")
        
        print("\n" + "=" * 50)
        sys.stdout.flush()
    
    def chiudi(self):
        """
        Chiude le connessioni.
        """
        if self.connessione:
            self.connessione.close()
        if self.socket:
            self.socket.close()
        print("\n[BOB] Connessione chiusa. Arrivederci!")
        sys.stdout.flush()



if __name__ == "__main__":
    print("=" * 50)
    print("   PROTOCOLLO ROSHAMBO SICURO - BOB (SERVER)")
    print("=" * 50)
    print()
    sys.stdout.flush()
    
    bob = Bob()
    try:
        bob.avvia_server()
        bob.accetta_connessione()
        bob.gioca()
    except KeyboardInterrupt:
        print("\n\n[BOB] Interruzione da tastiera...")
        sys.stdout.flush()
    except Exception as e:
        print(f"\n[BOB] Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
    finally:
        bob.chiudi()
        input("\nPremi INVIO per chiudere...")
