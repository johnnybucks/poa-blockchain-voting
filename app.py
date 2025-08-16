from flask import Flask, jsonify, request, render_template, redirect, url_for
import hashlib
import json
import time
import requests
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

app = Flask(__name__)

# Tentukan nama file kunci untuk node ini
private_key_filename = "node1_private.pem"
public_key_filename = "node1_public.pem"

ALLOWED_CANDIDATES = {"Candidate A", "Candidate B"}
# Memuat kunci privat
with open(private_key_filename, 'rb') as key_file:
    private_key = load_pem_private_key(key_file.read(), password=None)

# Memuat kunci publik
with open(public_key_filename, 'rb') as key_file:
    public_key = load_pem_public_key(key_file.read())

# Memuat daftar anggota yang valid
with open('membership_ids.json') as f:
    valid_members = {hashlib.sha256(member.encode()).hexdigest() for member in json.load(f)["members"]}

voted_members = set()

node_id = "node1"  # Ganti dengan ID node yang sesuai

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_votes = []
        self.create_block(proof=100, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'proof': proof,
            'previous_hash': previous_hash,
            'votes': self.pending_votes,
            'node_id': node_id  # Menambahkan asal node
        }
        self.pending_votes = []
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def add_vote(self, member_hash, candidate_id):
        vote = {
            'member_hash': member_hash,
            'candidate_id': candidate_id,
        }
        self.pending_votes.append(vote)
        return self.get_last_block()['index'] + 1

    def is_valid_member(self, member_id):
        member_hash = hashlib.sha256(member_id.encode()).hexdigest()
        return member_hash in valid_members

    def sign_vote(self, vote_data):
        signature = private_key.sign(
            vote_data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return signature

    def verify_vote(self, vote_data, signature):
        try:
            public_key.verify(
                signature,
                vote_data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

# Instansiasi blockchain
blockchain = Blockchain()

other_nodes = ["http://10.11.10.66:5000","http://10.11.10.248:5000","http://10.11.10.249:5000","http://10.11.10.250:5000"]  # Ganti dengan IP dan port node lain yang sesuai

def sync_with_other_nodes():
    global blockchain
    for node in other_nodes:
        try:
            response = requests.get(f"{node}/sync_chain")
            if response.status_code == 200:
                other_chain = response.json()["chain"]
                other_length = response.json()["length"]

                # Periksa jika node lain memiliki chain yang lebih panjang atau berbeda
                if other_length > len(blockchain.chain) or (other_length == len(blockchain.chain) and other_chain != blockchain.chain):
                    blockchain.chain = other_chain
                    print(f"Blockchain updated from {node}. New length: {other_length}")
        except requests.exceptions.RequestException as e:
            print(f"Could not synchronize with {node}: {e}")

@app.route('/')
def index():
    candidates = ['Candidate A', 'Candidate B']
    return render_template('index.html', candidates=candidates)

@app.route('/vote', methods=['POST'])
def vote():
    voter_id = request.form['voter_id']
    candidate_id = request.form['candidate']
    
    member_hash = hashlib.sha256(voter_id.encode()).hexdigest()

    if member_hash in voted_members:
        return render_template('index.html', candidates=['Candidate A', 'Candidate B'], message="You have already voted.")

    if not blockchain.is_valid_member(voter_id):
        return render_template('index.html', candidates=['Candidate A', 'Candidate B'], message="Invalid Membership ID.")
    
    if candidate_id not in ALLOWED_CANDIDATES:
        return render_template('index.html', candidates=list(ALLOWED_CANDIDATES), message="Invalid candidate.")

    vote_data = f"{member_hash}:{candidate_id}".encode()
    signature = blockchain.sign_vote(vote_data)
    blockchain.add_vote(member_hash, candidate_id)
    voted_members.add(member_hash)

    print("Before sync...")
    sync_with_other_nodes()
    print("After sync")

    # Buat dan simpan blok baru 
    last_block = blockchain.get_last_block()
    previous_hash = blockchain.hash_block(last_block)
    new_block = blockchain.create_block(proof=100, previous_hash=previous_hash)
    print("New Block Created:", new_block)

    block_hash = blockchain.hash_block(new_block)
    return render_template('vote_confirmation.html', block_hash=block_hash)

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.get_last_block()
    previous_hash = blockchain.hash_block(last_block)
    block = blockchain.create_block(proof=100, previous_hash=previous_hash)
    response = {
        'message': 'New block mined',
        'block': block,
    }
    return jsonify(response), 200

@app.route('/sync_chain', methods=['GET'])
def sync_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block)
    return jsonify({"chain": chain_data, "length": len(chain_data)}), 200

@app.route('/results', methods=['GET'])
def results():
    votes = []
    sync_with_other_nodes()
    for block in blockchain.chain:
        block_hash = blockchain.hash_block(block)
        node_origin = block['node_id']  # Ambil node_id dari block
        for vote in block['votes']:
            candidate_id = vote['candidate_id']  # Perbaiki akses ke `candidate_id`

            # Simpan setiap vote dengan block hash dan node_id
            votes.append({
                'block_hash': block_hash,
                'candidate': candidate_id,
                'node_id': node_origin
            })

    return render_template('results.html', votes=votes)

@app.route('/export', methods=['GET'])
def export_chain():
    """Export the blockchain as a JSON file."""
    return jsonify(blockchain.chain), 200    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
