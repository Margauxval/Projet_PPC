```mermaid
stateDiagram-v2
    [*] --> PASSIVE

    PASSIVE --> ACTIVE : energy < H
    ACTIVE --> PASSIVE : energy > H

    ACTIVE --> DEAD : energy < 0
    PASSIVE --> DEAD : energy < 0
