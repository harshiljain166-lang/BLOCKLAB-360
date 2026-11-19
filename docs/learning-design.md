# Learning Lab design

The UI ships structured lesson records for Beginner (block and hash), Intermediate (proof of work), and Advanced (distributed nodes and synchronization). Each lesson includes a concept, analogy, guided task, and backend-state verification. Completion is only awarded when the app checks live state: a non-genesis block exists for the block/PoW tasks, or all peers match the current height for the synchronization task.
