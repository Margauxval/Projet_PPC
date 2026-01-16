# Projet_PPC

1. **Modéliser l’écosystème**
   - **Définir les états et attributs** :
     - Prédateur : énergie, état (actif/passif), règles pour manger, se reproduire, mourir.
     - Proie : pareil, mais elle mange de l’herbe et peut être prédatée si active.
     - Herbe : quantité globale, croissance régulière sauf en période de sécheresse.
   - **Définir les seuils** :
     - Seuil \(H\) : en dessous → individu devient actif pour se nourrir.
     - Seuil \(R\) : au-dessus → individu peut se reproduire.
   - **Définir la dynamique** :
     - À chaque “tick” de temps : l’énergie baisse, certains mangent, certains se reproduisent, certains meurent, l’herbe pousse (sauf sécheresse).

2. **Concevoir l’architecture multiprocessus**
   - **Processus env** :
     - Contient la **mémoire partagée** avec les populations (nombre de prédateurs, de proies, quantité d’herbe, éventuellement plus de détails).
     - Gère le **climat** (sécheresse ou non).
     - Écoute sur un **socket** pour accepter de nouveaux processus predator/prey.
     - Réagit à un **signal** pour déclencher un épisode de sécheresse (par exemple : baisse ou arrêt de la croissance de l’herbe).
   - **Processus predator** :
     - Se connecte à env via le **socket** pour rejoindre la simulation.
     - Lit/écrit dans la **mémoire partagée** (avec synchronisation) pour savoir combien de proies il peut manger, etc.
     - Met à jour son énergie, décide de manger, se reproduire, mourir.
   - **Processus prey** :
     - Même logique que predator, mais avec l’herbe.
   - **Processus display** :
     - Communique avec env via une **file de messages**.
     - Affiche en temps réel les populations, l’état de la simulation.
     - Permet à l’utilisateur de **modifier des paramètres** (par exemple : taux de croissance de l’herbe, seuils H et R, nombre initial de prédateurs/proies).

3. **Choisir les mécanismes concrets en Python**
   - **Multiprocessing** pour les processus (module `multiprocessing`).
   - **Mémoire partagée** :
     - Par exemple `multiprocessing.Value`, `Array`, ou `Manager().dict()`/`Manager().list()` pour stocker les populations.
   - **Synchronisation** :
     - `multiprocessing.Lock`, `Semaphore`, etc. pour protéger l’accès à la mémoire partagée.
   - **Sockets** :
     - Module `socket` pour la communication entre env et predator/prey (TCP ou UDP, à toi de choisir et justifier).
   - **Message queue** :
     - `multiprocessing.Queue` ou une vraie file de messages (selon les contraintes du cours).
   - **Signaux** :
     - Module `signal` pour notifier env d’une sécheresse (par exemple `SIGUSR1`), avec un handler qui change un flag “drought = True”.

4. **Faire un diagramme et du pseudo-code**
   - **Diagramme de processus** :
     - Qui crée qui ? (env crée-t-il predator/prey, ou se connectent-ils indépendamment ?)
     - Comment circulent les infos (flèches entre env, predator, prey, display).
   - **Diagrammes d’états** :
     - Pour un individu : transitions entre actif/passif, vivant/mort, etc.
   - **Pseudo-code** :
     - Boucle principale de env.
     - Boucle principale de predator.
     - Boucle principale de prey.
     - Boucle principale de display.

5. **Plan de tests**
   - Tester **env seul** avec des valeurs en dur.
   - Tester **un predator** qui lit/écrit dans une mémoire partagée factice.
   - Tester **un prey** de la même façon.
   - Tester **env + display** avec une file de messages simple.
   - Tester **env + predator** via socket avec des messages simples (par exemple : “join”, “eat”, “reproduce”).
   - Puis assembler le tout et vérifier :
     - Que la simulation démarre proprement.
     - Que les processus se terminent proprement (pas de zombies, pas de ressources non libérées).


