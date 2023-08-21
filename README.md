# OAK Random Service

**OAK Random Service** is a crucial component in the process of OAK generation. It ensures that the OAK generation process is both fair and transparent. Specifically, this service is designed to randomly select tickets when the number of tickets for a given day surpasses the one-day limit.

## How it Works

1. **Seed Generation**: Call the smart contract to generate a seed. This can be done only once per round by any user.
2. **Random Data Generation**: With the seed, obtain random data off-chain using any compatible program. For instance, with Python, once the data is generated, check if your tickets are part of the selection.
3. **Admin Input**: Admins input the random data to the smart contract in batches. After all entries, you can verify your ticket's status either on the smart contract or via the OAK app.

## Running the Checker Script

To check the ticket status with our Python script:

### Prerequisites:

Ensure Python3 and pip3 are installed:

```bash
sudo apt-get update
sudo apt install python3-pip


Install the required Python packages:

​```bash
pip3 install web3


In case of any issues installing web3:

​```bash
python -m pip install --user cython
python -m pip install --user cytoolz
python -m pip install --user eth-brownie

### Execution:

Run the script:

​```bash
python3 oak_random_checking.py
```