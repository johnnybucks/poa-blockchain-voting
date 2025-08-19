# Blockchain Voting System

A blockchain-based e-voting system built with **Python** to ensure transparency, security, and fairness in the voting process.  
Each vote is recorded in a block, cryptographically signed, and synchronized across nodes.  
The system also generates a unique **receipt hash** for each voter (as proof of inclusion), allowing voters to verify that their vote has been recorded without exposing their identity.

---

## Features

- **Security**  
  Votes are validated using **public/private keys** and digital signatures.

- **Membership Validation**  
  Only authorized members (listed in `membership_ids.json`) are eligible to vote.

- **Anti-Duplication**  
  Each member can cast only **one vote**.

- **Candidate Filtering**  
  Votes are restricted to *Candidate A* or *Candidate B* (any payload manipulation is automatically rejected).

- **Immutable Blockchain**  
  Votes are stored in a tamper-proof blockchain ledger.

- **Multi-Node Synchronization**  
  The chain is synchronized across multiple nodes for data consistency.

- **Receipt Hash (ZKP-style)**  
  Each voter receives a unique hash upon casting a vote, which can be stored or scanned as proof that their vote has been successfully included in the blockchain (without revealing identity).
