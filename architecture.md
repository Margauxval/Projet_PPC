```mermaid
flowchart LR
    Display -->|Message Queue| Env
    Env -->|Shared Memory| Predator
    Env -->|Shared Memory| Prey

    Predator -->|Socket join| Env
    Prey -->|Socket join| Env

    OS -->|SIGUSR1 drought| Env
