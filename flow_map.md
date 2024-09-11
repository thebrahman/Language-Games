graph TD
    A[Start] --> B[Initialize System]
    B --> C[Load Initial Game State]
    C --> D[Start turn]

    subgraph "Environment and NPC Processing"
        D --> DE1[Environment System Prompt]
        D --> DE2[Game State]
        DE1 --> E1[Environment LLM Processing]
        DE2 --> E1
        D --> DN1[NPC System Prompts]
        D --> DN2[Game State]
        DN1 --> E2[NPC LLMs Processing]
        DN2 --> E2
        E1 --> F1[Environment Game State Output]
        E2 --> F2[NPC Game state Output]
    end

    F1 --> G[Interaction LLM processing]
    F2 --> G
    
    G --> H[updated game state]
    H --> I[Parse Interaction Output]
    
    subgraph "Prompt and State Updates"
        I --> J1[Update Environment System Prompt]
        I --> J2[Update NPC System Prompts]
        I --> J3[Update Game State]
    end

    J1 --> K[End Turn]
    J2 --> K
    J3 --> K

    K --> |Next Turn| D