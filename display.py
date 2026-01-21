import pygame
import time
from pygame.locals import *

def show_bilan(screen, font_l, font_s, texte_bilan):
    """Affiche l'écran final de statistiques."""
    running = True
    while running:
        screen.fill((20, 50, 20))
        screen.blit(font_l.render("=== BILAN FINAL ===", True, (255, 255, 255)), (250, 150))
        
        parts = texte_bilan.split(" | ")
        for i, part in enumerate(parts):
            screen.blit(font_s.render(part, True, (200, 255, 200)), (150, 250 + i * 40))

        screen.blit(font_s.render("Appuyez sur une touche pour quitter", True, (150, 150, 150)), (250, 500))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type in (QUIT, KEYDOWN):
                running = False

def display_process(msg_queue):
    """Processus d'affichage utilisant uniquement la Message Queue."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Circle of Life - EcoSim")

    font_large = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    logs = []
    last_status = "Initialisation..."

    while True:
        # 1. Gestion des entrées utilisateur
        for event in pygame.event.get():
            if event.type == QUIT:
                msg_queue.put(("CMD", "STOP"))
                return
            if event.type == KEYDOWN:
                if event.key == K_q:
                    msg_queue.put(("CMD", "STOP"))
                elif event.key == K_d:
                    msg_queue.put(("CMD", "FORCED_DROUGHT"))

        # 2. Lecture d'UN SEUL message à la fois pour éviter l'effet "bloc"
        # On utilise get_nowait() pour ne pas bloquer le rendu graphique
        try:
            msg = msg_queue.get_nowait()

            if msg == "STOP": 
                return
            
            if isinstance(msg, tuple) and msg[0] == "BILAN":
                show_bilan(screen, font_large, font_small, msg[1])
                return

            if isinstance(msg, str):
                if "|" in msg: 
                    # Mise à jour instantanée du bandeau de statut (Herbe/Proies/Pred)
                    last_status = msg
                else: 
                    # Ajout d'une action dans les logs (Naissance/Mort/Manger)
                    logs.append(msg)
                    if len(logs) > 16: 
                        logs.pop(0)
                    
                    # --- RALENTISSEMENT ---
                    # On attend un peu après avoir reçu une action pour qu'elle soit lisible
                    time.sleep(0.15) 
        except:
            # Pas de message dans la queue, on continue le rendu
            pass

        # 3. Rendu Graphique
        screen.fill((30, 30, 30))

        # Bandeau de Statut (Haut)
        pygame.draw.rect(screen, (50, 50, 80), (20, 20, 760, 60))
        screen.blit(font_large.render(last_status, True, (255, 255, 0)), (40, 38))

        # Zone des Logs (Milieu)
        for i, log in enumerate(logs):
            color = (200, 200, 200) # Gris par défaut
            if "mangé" in log or "Naissance" in log: 
                color = (100, 255, 100) # Vert
            if "PRÉDATION" in log or "mort" in log: 
                color = (255, 100, 100) # Rouge
            screen.blit(font_small.render(f"> {log}", True, color), (50, 110 + i * 25))

        # Bandeau d'Instructions (Bas)
        pygame.draw.rect(screen, (20, 20, 20), (0, 560, 800, 40))
        instructions = font_small.render("[D] Forcer Sécheresse | [Q] Quitter", True, (255, 255, 255))
        screen.blit(instructions, (50, 572))

        pygame.display.flip()
        clock.tick(30)
