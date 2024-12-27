In memory database just for fun:

- WAL
  - wal file, is a text file where every operation is a json object
  - snapshot file, is a binary file, a pickled version of the loaded database

- Operations
  - append to the log file
  - construct the db from the log file
  - create a snapshot file
  - load from a snapshot file

- Implement transactions
- Implement concurrency, lock ?


Functions:
- Insert
  - Find which node to add to
  - Adding to a free node
  - Adding to a full node
    - Detect overflow on the node
    - Split a node:
      - Modify keys on first node and create a second node
      - Create parent if needed
      - Add new children to parent
    - Add middle key to parent 
    - If current node is internal delete the key
    - Handle parent overflow recursively
      - Detect overflow on non leaf
      - Call split a node and middle key things
      - Split children and add to parent
